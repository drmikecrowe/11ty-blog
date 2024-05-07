---
title: How Can I Wordle Out of Housework
date: 2022-03-06
excerpt: I'm obsessing about the best wordle start words
tags:
  - tech
  - typescript
  - statistics
author: mike-crowe
draft: 
seo:
  title:
  description: typescript analysis of wordle words
  image: 2023/03/screenshot-www.nytimes.com-2022.03.06-06_32_37.png
images: # relative to /src/assets/images/
  feature: 2023/03/screenshot-www.nytimes.com-2022.03.06-06_32_37.png
  thumb: 2023/03/screenshot-www.nytimes.com-2022.03.06-06_32_37.png
  slide:
---

Let me start this with a confession:

> **I don’t (technically) play Wordle**

This is very important, as recently my wife came to me and proclaimed “I just got a “magnificent” in Wordle” (the blank look on my face definitely bumped up my heating bill for a few days). When I asked my daughter if she played it, she pointed me to [Word Master](https://octokatherine.github.io/word-master/) and I was hooked.

Many discussions (with my daughter — my wife had no interest in our flagrant disrespect of Wordle) ensued about the best words to start. For the longest time, mine were `train`, `speck`, `dough`. You see, our philosophy was to bang out 2-3 words and get the letters, then stress over guessing the word after establishing a good set of letters (hopefully in the right position). I searched online for the best 3 words, but nobody seemed to follow this technique. Everybody writing about this only was interested in the best _first_ word. So, off I went to figure it out.

But first, take another look at `octokatherine`‘s creation: Open source, hosted in github, quite a few contributors, pull-requests, issues. Wow, just wow.

The idea of a blog post started in the idle thought of, “how would you determine the top 3 best words to start with?”

Then it spiraled into thoughts of recursion (determine the best first word, then all the best second words, etc). I then realized that I needed to jump into it and start this because I was going to obsess about it in my head until I did.

If you are of a technical nature, keep reading. If you want to see my thoughts about the best start words, jump to the bottom…

The first challenge was determining how to track letters. I came up with this class:

```ts
export class Letter {
  letter: string;
  words: string[] = [];
  occurrences: number = 0;
  positions: number[] = [0, 0, 0, 0, 0];
  bestPosition: number = 0;
  rank: number = 0;

  constructor(letter: string) {
    this.letter = letter;
  }

  addWord(word: string) {
    this.words.push(word);
  }

  bumpPosition(offset: number) {
    this.positions[offset]++;
    this.occurrences++;
    this.bestPosition = this.positions.indexOf([...this.positions].sort((a, b) =&gt; b - a)[0]);
  }
}
```

So, for each letter I tracked:

- `words`: All words that contain this letter
- `occurrences`: The total number of times this letter appears in all words
- `positions`: The total number of times a letter appears in a specific position in the word
- `bestPosition`: The most frequent position for this word
- `rank`: The relative ratio of the number of occurrences of this word vs. all letters

Next, configured all the structures with some code:

```ts
const letterMap: Record&lt;string, Letter&gt; = {}
ALL_LETTERS.forEach((letter) =&gt; {
  letterMap[letter] = new Letter(letter);
});
const letterList: Letter[] = Object.values(letterMap);
```

Next, we need to add all the words to the system:

```ts
  wordList.forEach((word) =&gt; {
    const letters = toLetterAry(word);

    letters.forEach((letter, i) =&gt; {
      // For stats, use all words
      letterMap[letter].bumpPosition(i);

      // Don't bother with words that have duplicate letters
      if (letters.length === 5) letterMap[letter].addWord(word);
    })
  });
  ALL_LETTERS.forEach((letter) =&gt; {
    letterMap[letter].rank = letterMap[letter].occurrences / totalLetters;
  });

  letterList.sort((a, b) =&gt; b.occurrences - a.occurrences);
  sortedLetters = letterList.map((l) =&gt; l.letter);
  bestLetters = sortedLetters.slice(0, 15);
```

Good. Now we can see our stats for a given letter. Here are the most common letters _**for the word list used by WordMaster!**_ (I don’t have access to the actual Wordle word list)

![screenshot](/assets/images/2023/03/2022-03-05_12-21.png)

This output is from the awesome [debug](https://github.com/debug-js/debug) library — run:  
`DEBUG=letters:verbose ts-node -T index.ts`

The next challenge was to build a list of all the words to check in the 3 positions. First, I came up with the following function to gather words that did NOT have a list of letters in them:

```ts
function Available(letters: string[] = []): string[] {
  const in_common = (a: string | string[], b: string | string[]): number =&gt;
    toLetterAry(a).filter((x) =&gt; toLetterAry(b).includes(x)).length;

  const all = letterList
    .slice(0, 15)
    .reduce((acc: string[], cur) =&gt; acc.concat(cur.words.filter((word) =&gt; in_common(word, bestLetters) === 5)), [])
    .filter((word) =&gt; in_common(letters, word) === 0);
  const res = [...new Set(all)];
  log_avail(`For ${letters.join(",")} we found ${res.length} words`);
  return res;
}
```

This grabs the `words` list from all the best 15 letters.

Key points:

- The `reduce` block concats all 15 word list into a single array
- The `filter` block removes words that have any letters in common with the `letters` parameters

First time I computed the list of available words it returned ~2100 words. As you’ll see shortly, this resulted in a massive outer loop that would take over 4h to run! To simplify, I decided (just for development while I’m coding) to assume the best words to start with would have the first 7 letters only. That reduces the out loop to 133, and it will only take about 20m to run. Much better.

Next, how to build the word list? Here’s what I came up with:

```ts
for (const word1 of [...Available(bestLetters.slice(8))]) {
  for (const word2 of [...Available(toLetterAry(word1))]) {
    for (const word3 of [...Available(toLetterAry(word1 + word2))]) {
      const words = [word1, word2, word3].sort((a, b) =&gt; Rank(b) - Rank(a));
      const key = words.join(",");
      const result: Results = {
        words,
        rank: Rank(word1) + Rank(word2) + Rank(word3),
        posHits: __, // number of best position hits, computation omitted for brevity
        output: `${key}: rank=${detail.combRank.toFixed(1)}, posHits=${detail.posHits}`,
      };
      let found = false;
      const myRank = keyToRank(words);
      for (let [i, existing] of results.entries()) {
        if (myRank &gt; existing.rank) {
          results.splice(i, 0, result);
          found = true;
          break;
        }
      }
      if (!found) results.push(result);
    }
  }
}
```

You can see here where I limited the outer loop — the inner loops are pretty small.

Now we need some type of ranking function. Here’s my first pass:

```ts
function Rank(word: string): number {
  const letters = toLetterAry(word);
  let posHits = 0;
  let rank = 0;
  for (const [pos, letter] of letters.entries()) {
    rank += letterMap[letter].rank;
    if (pos === letterMap[letter].bestPosition) {
      rank += RIGHT_POS_RANK;
      posHits++;
    }
  }
  log_rank(`${word} has rank ${rank}`);
  return rank;
}
```

This was OK but had some problems I’ll detail in a moment. It used the accumulated letter rank as the base rank, then an arbitrary adjustment for having the letter in the right position (`RIGHT_POS_RANK` — for the first pass, I set this to `0.3`).

The first real results looked like this:

```ts
[
  'tiles,dunam,porch: rank=4.1, posHits=11',
  'tiles,dunam,porch: rank=4.1, posHits=11',
  'tires,dolma,punch: rank=4.1, posHits=11',
  'tires,dolma,punch: rank=4.1, posHits=11',
  'toles,diram,punch: rank=4.1, posHits=11',
  'toles,pardi,munch: rank=4.1, posHits=11',
  'toles,pardi,munch: rank=4.1, posHits=11',
  'toles,diram,punch: rank=4.1, posHits=11',
  'tores,milpa,dunch: rank=4.1, posHits=11',
  'tores,milpa,dunch: rank=4.1, posHits=11'
]
```

The more I thought about this, the more I realized this was considering all 3 words in the same weight (i.e. the 3rd word contributes just as much to its position _in the result array_ as the first word. That’s not right.

Ideally, we need the first word to have the most weight, followed by the second, then 3rd word. Additionally, it also looks like my `RIGHT_POS_RANK` is too high — seems like it’s skewing the results too much (open call to any math majors who want to help me analyze how much weight to apply here).

So, the next revision of the ranking function is:

```ts
function Rank(word: string): number {
  const letters = toLetterAry(word);
  let posHits = 0;
  let rank = 0;
  for (const [pos, letter] of letters.entries()) {
      let r = letterMap[letter].rank;
      if (pos === letterMap[letter].bestPosition) {
        r *= 2;
        posHits++;
      }
      rank += r;
  }
  log_rank(`${word} has rank ${rank}`);
  return rank;
}
```

Instead of an arbitrary weight for being in the right position, I doubled the value of the character weight.

Additionally, I chose to weigh the word position as follows:

- First word: 60%
- Second word: 25%
- Third word: 15%

In the code, that looks like this:

```ts
...
      const result: Results = {
        words,
        rank: Rank(word1) * 0.6 + Rank(word2) * 0.25 + Rank(word3) * 0.15,
        posHits: __, // number of best position hits, computation omitted for brevity
        output: `${key}: rank=${detail.combRank.toFixed(1)}, posHits=${detail.posHits}`,
      };
...
```

Overall, this seems like a better fit. Here’s the final word list using this revised code, and using _all_ words instead of the first set:

```ts
[]
```

Argh — after 4h and the time extending, I need to review the code and optimize. This is a common situation: Initial code is never optimized. When you add a full data set, you often find ways to improve it.

Here are bottlenecks I found:

- Don’t try and build _and process_ the entire list of word combinations — break that into two steps. There are ~127k combinations of 3 words using the best letters for the 10k words
- Don’t do things in your processing loop that you can do in advance. I filtered down the 10k words to those I’m interested in (they have the 15 most common letters only).
- Cache, cache, cache. I realized that the available words could be cached if you sort the letters you are looking for. If you think about it, the available words for the word combinations:
  - ‘acidy’, ‘prost’
- is the same as the words for:
  - ‘acidy’, ‘sport’

Now the loop runs in seconds. I wouldn’t have minded it taking a while to compute, but after the optimization step, I’m pleased.

After discussions with another [Pinnacle consultant,](https://pinnsg.com/consultant/kevin-rohr/) we brainstormed on how to weigh the position. In thinking about it, we could accumulate the weights per position and add that ratio to the total. For instance, consider the letter A in this word:

![Letter a weights](/assets/images/2023/03/2022-03-07_12-27-position-weight.png)

Letter A weights

As you can see, the letter `a` occurs 3788 times in all the words, and it appears most frequently in position 2 (everything in JavaScript is offset 0 based). So, if `a` occurs in position 1, we would add an additional `0.4242...` weight to the rank. Since all words appear somewhere, I like this idea for normalizing the location of the weight.

Additionally, he pointed out that we really want more vowels since those are vital to a word. In the above image, you can see I’m adding `0.4` because it’s a vowel.

This analysis runs quickly, so I created a [weights.json](https://github.com/drmikecrowe/wordle-blog/blob/master/weights.json) for toying with the weights.

## The Results (so far) based on My preferences

Here are the top 5 word combinations, including the ranking and number of times the letters are in the right space:

```ts
    "soare,clint,dumpy: rank=0.62, 0.82/0.38/0.27, posHits=5",
    "toeas,rindy,clump: rank=0.62, 0.82/0.38/0.28, posHits=7",
    "aides,porny,mulct: rank=0.61, 0.81/0.40/0.31, posHits=10",
    "toeas,lindy,crump: rank=0.61, 0.82/0.37/0.29, posHits=7",
    "aeons,dirty,clump: rank=0.61, 0.81/0.39/0.28, posHits=6",
    "tares,colin,dumpy: rank=0.61, 0.76/0.49/0.27, posHits=11",
```

Legend:

- Ranks show how each word contributed to the overall rank
- posHits show how many letters are in the most favorable position in the top 3 words

You can find all the code for this [here](https://github.com/drmikecrowe/wordle-blog).
