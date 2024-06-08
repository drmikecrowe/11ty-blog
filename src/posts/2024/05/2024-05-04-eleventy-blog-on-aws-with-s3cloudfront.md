---
title: Eleventy Blog on AWS with S3/CloudFront
description: ""
date: 2024-05-04T23:36:31.476Z
preview: ""
draft: false
categories: 
  - pinnacle
type: default
excerpt: "This post is about setting up an Eleventy blog with AWS S3 and CloudFront.  It took a bit of digging to get working, so I'm writing it down for posterity.  The key was to configure the CloudFront origin to the s3 _website_ endpoint, not the s3 domain itself."
tags:
  - tech
  - eleventy
  - aws 
  - pulumi
  - pinnacle
author: mike-crowe
seo:
  title:
  description: 
  image: 2024/05/2024-05-04-hero.webp 
images:
  feature: 2024/05/2024-05-04-hero.webp
  thumb: 2024/05/2024-05-04-hero.webp
  slide:
---

In starting this blog, I wanted to use AWS S3/CloudFront. I initially investigated [SST (ion specifically)](https://ion.sst.dev).  However, I kept running into issues with SST and NixOS, so I bailed on SST and moved directly to [Pulumi](https://www.pulumi.com).  Pulumi is a Terraform competitor, and I have been curious to try it out.

They have a static [site starter](https://github.com/pulumi/examples/tree/master/aws-ts-static-website).  This is actually a decent start, but I ran into a few problems deploying my new [Eleventy Blog](https://www.11ty.dev).  The home page worked fine, but as you drive into sub-folders (like `/blog/`), I started getting 403 Forbidden errors.

Here's their original code:

```ts
    origins: [
        {
            originId: contentBucket.arn,
            domainName: contentBucket.bucketRegionalDomainName,
            s3OriginConfig: {
                originAccessIdentity: originAccessIdentity.cloudfrontAccessIdentityPath,
            },
        },
    ],
```

However, this is configuring the CloudFront origin to the s3 domain, not the _website_ endpoint that is actually required.  Through much weeping and gnashing of teeth, I finally got this configuration working:

```ts
    origins: [
        {
            originId: contentBucket.arn,
            domainName: contentBucket.websiteEndpoint,
            customOriginConfig: {
                httpPort: 80,
                httpsPort: 443,
                originProtocolPolicy: 'http-only',
                originSslProtocols: ['TLSv1.2'],
                originReadTimeout: 30,
                originKeepaliveTimeout: 5,
            },
        },
    ],
```

In other words, `s3OriginConfig` can't be used because you can't use the `websiteEndpoint`.  You have to switch to a `customOriginConfig` output instead.

Additionally, when you do this, you can no longer use ACL's to grant CloudFront access to your s3 bucket -- I made it public-read instead.  I'm sure there's a bucket policy that could keep the S3 bucket private, but it's a public blog anyway.
