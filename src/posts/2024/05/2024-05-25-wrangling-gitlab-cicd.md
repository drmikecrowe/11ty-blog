---
title: Wrangling Gitlab CI/CD in Monorepos
description: "Managing monorepo node-modules cache, Using Anchors, Stages and Dependencies, and other weird quirks of Gitlab's CI/CD Engine."
date: 2024-05-25
updated:
  - ''
preview: ''
draft: false
categories:
  - Pinnacle
type: default
excerpt: ''
tags:
  - Gitlab
  - CI/CD
  - pinnacle
author: mike-crowe
seo:
  title: ''
  description: ''
  image: ''
images:
  feature: '2024/05/kelly-sikkema-lFtttcsx5Vk-unsplash.jpg'
  thumb: '2024/05/kelly-sikkema-lFtttcsx5Vk-unsplash.jpg'
  slide: ''
---
> <small>Photo by <a href="https://unsplash.com/@kellysikkema?utm_content=creditCopyText&utm_medium=referral&utm_source=unsplash">Kelly Sikkema</a> on <a href="https://unsplash.com/photos/a-person-drawing-a-diagram-on-a-piece-of-paper-lFtttcsx5Vk?utm_content=creditCopyText&utm_medium=referral&utm_source=unsplash">Unsplash</a></small>


So, I recently had the opportunity to extensively dig into Gitlab’s CI/CD. We have a monorepo that I wanted to deploy automatically, and it took quite a bit of work to optimize it and work as I expected.

To set the stage, here's our core `.gitlab-ci.yml` file (now):

```yaml
image: node:18-alpine3.19

variables:
  AWS_REGION: us-east-1
  AWS_DEFAULT_REGION: us-east-1
  FF_USE_FASTZIP: 'true'
  ARTIFACT_COMPRESSION_LEVEL: 'fast'
  CACHE_COMPRESSION_LEVEL: 'fast'

stages:
  - prepare
  - module-caches
  - layers
  - build
  - deploy

#******************************************************************

include:
  - local: '.gitlab/cache-ci.yml'
  - local: '.gitlab/rules-ci.yml'
  - local: '.gitlab/build-ci.yml'
  - local: '.gitlab/deploy-ci.yml'
  - local: 'apps/landing/.gitlab-cache-ci.yml'
  - local: 'apps/landing/.gitlab-ci.yml'
  - local: 'apps/quickbooks-connector/.gitlab-ci.yml'
  - local: 'apps/reviews/reviews-api/.gitlab-cache-ci.yml'
  - local: 'apps/reviews/reviews-api/.gitlab-ci.yml'
  - local: 'apps/reviews/reviews-ui/.gitlab-cache-ci.yml'
  - local: 'apps/reviews/reviews-ui/.gitlab-ci.yml'
  - local: 'apps/stocks/stocks-api/.gitlab-cache-ci.yml'
  - local: 'apps/stocks/stocks-api/.gitlab-ci.yml'
  - local: 'apps/stocks/stocks-ui/.gitlab-cache-ci.yml'
  - local: 'apps/stocks/stocks-ui/.gitlab-ci.yml'
  - local: 'apps/tnb/tnb-api/.gitlab-cache-ci.yml'
  - local: 'apps/tnb/tnb-api/.gitlab-ci.yml'
  - local: 'apps/tnb/tnb-ui/.gitlab-cache-ci.yml'
  - local: 'apps/tnb/tnb-ui/.gitlab-ci.yml'
  - local: 'packages/pinnacle-layer/.gitlab-cache-ci.yml'
  - local: 'packages/pinnacle-layer/.gitlab-ci.yml'

# variables:
#   CI_DEBUG_TRACE: true

#******************************************************************

always:
  stage: prepare
  script:
    - env | sort
```

Here are some of the things that drove me crazy:

- Anchors are only valid in the current yaml file
- Don't use needs -- use stages instead
- Caching in Gitlab works great, but you need to specify your cache in right order
- You can only create/use 4 separate caches per job

Here are some details on these to hopefully help you out in the future.

## Anchors

Anchors are tremendously useful. If you haven't used them before, anchors in a yaml file can give you the ability to, in effect, memorize a block of yaml and later in the file, use that yaml without having to cut and paste it. Here is an example:

```yaml
.yarn-global-cache: &yarn-global-cache
  key: $CI_MERGE_REQUEST_SOURCE_BRANCH_NAME$CI_COMMIT_BRANCH-global-cache
  paths:
    - .yarn/install-state.gz
    - .yarn/cache
    - node_modules

.push-yarn-global-cache:
  cache:
    - policy: pull-push
      unprotect: true
      <<: *yarn-global-cache

.pull-yarn-global-cache:
  cache:
    - policy: pull
      unprotect: true
      <<: *yarn-global-cache
```

So, as you can see here, I only define my cache paths once, but I can use them in multiple places.

Here's where I ran afoul of the same-file issue. In the above code, I really wanted to use `yarn-global-cache` elsewhere in my pipeline. However, since it's an anchor, its scope is only this local file.
Gitlab has an alternative though, which you can see here. Anywhere I want to use this cache, all i have to do is:

```yaml
  extends:
    - .pull-yarn-global-cache
```

This will essentially include the same code as above into your current block of code. Seems ideal, right? Well, here's the rabbit hole I went down:

Our internal applications are a set of websites/microservices that handle our day/day operations like time and billing, expense reports, employee reviews, etc. Each of these we've designed to be a static website, talking about microservice for simplicity. All of them are currently written in TypeScript and use the serverless framework as the back-end. I was looking at the six repos that made three applications, each having a front end and a back end, and thought a monorepo would make this so much easier to manage. It did, but that took a lot of pain to get to where it was easy.
When you're developing a node project, your `node_modules` folder houses all of the dependencies for your application. In a monorepo, it's a bit more complex because you have a couple of choices about how you want each project to store its `node_modules`. What I wanted to do is to leverage some of the newer strategies and use a technique called PNP that `yarn` and `pnpm` use. On the one hand, this new mode definitely speeds up the CI/CD process. However, a lot of the tooling for a Node project does not support this. The straw that broke the camel's back for me was when we started experimenting with Svelte and they categorically said they would never support PNP. At that point, I had to rip out all of that tooling and start from scratch again trying to figure out how to use the traditional `node_modules`. Thus began the journey into Gitlab caching.

## Needs vs Stages

As you will see in the caching section coming next, the dependencies can get complicated when trying to orchestrate a monorepo deployment. I initially thought that I could use the `needs` construct to specify which job I was waiting for. It seemed easy. Before building the project, specify that it needs its `node_modules`. Then specify that the `node_modules` need the global `node_modules`. For example, I was trying to stage my caches like this:

```yaml
prepare:global-cache:
  extends:
    - .push-yarn-global-cache
  stage: prepare
  script:
    - yarn set version 4.1.1 && yarn install --immutable
  rules:
    - if: $CI_PIPELINE_SOURCE == "push"
      changes:
        - .yarn/install-state.gz
        - yarn.lock

prepare:global-cache2:
  extends:
    - .push-yarn-global-cache2
  stage: prepare
  needs:
    - prepare:global-cache
  script:
    - yarn set version 4.1.1 && yarn install --immutable
  rules:
    - if: $CI_PIPELINE_SOURCE == "push"
      changes:
        - .yarn/install-state.gz
        - yarn.lock

```

so `prepare:global-cache` fed into `prepare:global-cache2` and then into `prepare:global-cache3`, etc.  However, the minute you use `needs`, you abandon stages globally and you must use `needs` everywhere.  That wasn't really ideal.

Instead, use the `stages` construct. This is what it is really built for anyway. What I broke my project into were the following stages:

- `prepare` -- this builds the top-level `node_modules` and `~/.yarn/cache` folders and caches them
- `modules-cache` -- this builds in the individual project `node_modules` folders
- `layers` -- this deploys our lambda layer (speeds up our lambda cold-starts)
- `deploy` -- this deploys each application
  By putting each job in the correct stage, no job will start until the prior stage is finished. For a good visual representation, here's an example deployment:

![screenshot](/assets/images/2024/05/2024-05-05-example-stages.png)
  
Each project requires its `node_modules` and the global layer to be built first. By using stages, these are sequenced as a group, and the corresponding `.gitlab-ci.yaml` is simplified.

## Caching done wrong

First off, the tooling for a node-based project concerning monorepos has come a long way. However, it still has some quirks that are frankly frustrating. After a lot of trial and error, I went back to the classic installation mode where each project has its own `node_modules` folder. I didn't want to use this method, but after repeated failures with different tools like ESLint and certain plugins related to that failing, I had no other choice than to go back to the classic installation mode. Hopefully, in the future, this will get better, but for automated deployments, it was the most reliable.
If I simply did a yarn install in the CI/CD pipeline, this would burn up four, five, or even six minutes of our pipeline just to install our `node_modules`. Even if I cached all of the sources in the `.yarn/cache`, it still was a significant part of the build process that I wanted to optimize. That left me with the following folders to cache:

```log
./node_modules
./apps/reviews/reviews-api/node_modules
./apps/reviews/reviews-ui/node_modules
./apps/stocks/stocks-api/node_modules
./apps/stocks/stocks-ui/node_modules
...
```

One of my first routes was using the anchors like this:

```yaml
.yarn-reviews-api-modules: &yarn-reviews-api-modules
  key: $CI_COMMIT_BRANCH-reviews-api
  paths:
    - .yarn/install-state.gz
    - ./apps/reviews/reviews-api/node_modules

.yarn-reviews-ui-modules: &yarn-reviews-ui-modules
  key: $CI_COMMIT_BRANCH-reviews-ui
  paths:
    - .yarn/install-state.gz
    - ./apps/reviews/reviews-ui/node_modules
```

Then I could do one `yarn install --immutable` and cache things:

```yaml
.push-yarn-global-cache:
  cache:
    - policy: pull
      unprotect: true
      <<: *yarn-global-cache
    - policy: pull-push
      unprotect: true
      <<: *yarn-reviews-api-modules
    - policy: pull-push
      unprotect: true
      <<: *yarn-reviews-ui-modules](<cache:
    - policy: pull-push
      unprotect: true
      %3C<: *yarn-global-cache
    - policy: pull-push
      unprotect: true
      <<: *yarn-tnb-ui-modules
    - policy: pull-push
      unprotect: true
      <<: *yarn-tnb-api-modules
    - policy: pull-push
      unprotect: true
      <<: *yarn-reviews-api-modules
    - policy: pull-push
      unprotect: true
      <<: *yarn-reviews-ui-modules
    - policy: pull-push
      unprotect: true
      <<: *yarn-stocks-api-modules
    - policy: pull-push
      unprotect: true
      <<: *yarn-stocks-ui-modules>
```

Then for each sub-project, all I would have to do is:

```yaml
deploy-reviews-api dev:
  extends:
    - .vars-reviews-api
    - .deploy
    - .rule-deploy-dev
    - .pull-yarn-reviews-api-modules
```

And I would be set. Unfortunately, I ran into a couple of problems. First, Gitlab only lets you create four caches during any build. I worked around that by grouping the caches into three stages of four to handle our eleven internal projects, but then I ran into a different problem. The order matters. If I created the cache in this order (this only needs to be done once for each version of `yarn.lock`):

#### node_modules push example

- `global-cache`
- `reviews-api`
- `reviews-ui`
- `stocks-api`

  But I tried to retrieve them in this order (say when the `stocks-api` project is building):

#### project build example

- `global-cache`
- `stocks-api`

  The `stocks-api` cache would fail, because when I created it, they suffix the cache key with `_4` (in my push example above). But, in the project build example, it would try to pull with a cache key suffixed with a `_1`, thereby failing. What a PITA.

## Caching done right

So, what's the right solution? What I finally landed on is the following:

The `node_modules` folder doesn't change frequently, and it is also typically linked to a branch. So I created a cache for each branch in the monorepo according to a unique branch name + `yarn.lock`. Then, when the branch is first pushed to Gitlab, each project will build its local `node_modules` and cache them. As you can see from before, I tried to just do four builds to get my 11 `node_modules` caches, but for both simplicity and ease of maintenance, I changed to actually do each project's build independently.

Impact? Some. I went from 4 jobs running per new branch update to 11. However, the simplicity was a big win. Further, by adopting a common pattern for each project, I was able to create a template for each project and automate the cache creation. Here's how:

- First, I created a template for a given module that would build every project's `node_modules` in a similar fashion:

```sh
cat <<EOF > $FOLDER/.gitlab-cache-ci.yml
.yarn-global-cache: &yarn-global-cache
  key: \$CI_MERGE_REQUEST_SOURCE_BRANCH_NAME\$CI_COMMIT_BRANCH-global-cache
  paths:
    - .yarn/install-state.gz
    - .yarn/cache
    - node_modules

.yarn-$MODULE-modules: &yarn-$MODULE-modules
  key: \$CI_MERGE_REQUEST_SOURCE_BRANCH_NAME\$CI_COMMIT_BRANCH-$MODULE
  paths:
    - $FOLDER/node_modules
    $MORE_FOLDERS

.pull-yarn-$MODULE-modules:
  cache:
    - policy: pull
      unprotect: true
      <<: *yarn-global-cache
    - policy: pull
      unprotect: true
      <<: *yarn-$MODULE-modules

.push-yarn-$MODULE-modules:
  cache:
    - policy: pull
      unprotect: true
      <<: *yarn-global-cache
    - policy: pull-push
      unprotect: true
      <<: *yarn-$MODULE-modules

module-caches:$MODULE-cache:
  extends:
    - .push-yarn-$MODULE-modules
  stage: module-caches
  script:
    - yarn prepare
  rules:
    - if: \$CI_PIPELINE_SOURCE == "push"
      changes:
        - .yarn/install-state.gz
        - yarn.lock
        - .trigger-build
        - $FOLDER/.trigger-module-cache-build
EOF
```

- Each project has its build recipe and its `node_modules` recipe:

```yaml
include:
  - local: '.gitlab/cache-ci.yml'
  - local: '.gitlab/rules-ci.yml'
  - local: '.gitlab/build-ci.yml'
  - local: '.gitlab/deploy-ci.yml'
  - local: 'apps/landing/.gitlab-cache-ci.yml'
  - local: 'apps/landing/.gitlab-ci.yml'
  - local: 'apps/reviews/reviews-api/.gitlab-cache-ci.yml'
  - local: 'apps/reviews/reviews-api/.gitlab-ci.yml'
```

- Within each build script:

```yaml
.vars-reviews-api:
  variables:
    MODULE_NAME: reviews-api
    MODULE_PATH: apps/reviews/reviews-api

.deploy-reviews-api:
  stage: deploy
  script:
    - cd $MODULE_PATH
    - yarn run deploy-${CI_ENVIRONMENT_SLUG}

build-reviews-api:
  extends:
    - .build
    - .vars-reviews-api
    - .rule-merge-request
    - .pull-yarn-reviews-api-modules

deploy-reviews-api dev:
  extends:
    - .vars-reviews-api
    - .deploy-reviews-api
    - .rule-deploy-dev
    - .pull-yarn-reviews-api-modules

deploy-reviews-api prod:
  extends:
    - .vars-reviews-api
    - .deploy-reviews-api
    - .rule-deploy-prod
    - .pull-yarn-reviews-api-modules
```

As you can see, this greatly simplified my deployment process by using these `extends` construct and making the cache templates. This went from something that was very bug-ridden to a repeatable process that is actually fast. A given deployment only takes 1-2 minutes for a code change now because of how well we are caching.
