---
name: news-dedup
description: Use when checking whether the current list of news articles contains duplicates. Removes duplicate news from the current list.
---

# news-dedup

## Steps

1. Compare the articles in the current list and check for duplicate or similar news content.
2. If the current list contains duplicate news content, remove the lower-quality duplicates from the list.
3. Return the structured list of news articles with no duplicates.

## Examples

News 1: Company A released new product X, expected to launch next month.
News 2: Company A's X is planned to launch next month. Its features and functions are also described.
Both articles cover the same story and count as duplicates. The lower-quality one is removed. News 2 has richer content, so keep News 2 and remove News 1.

News 3: Company A's X. Its market positioning and sales strategy are described in detail.
This article is similar to News 1 and News 2 but has a different focus, so it is not a duplicate.

News 4: Features and functions of Company A's new product X.
Compare this article with News 1 and News 2. If the content is highly similar and the focus is the same, it also counts as a duplicate. When the quality is about the same, keep any one of them.

## Edge cases

- If the current list is empty, return an empty list.
- If every article in the current list duplicates another one, return a single article.
- If the current list contains only one article, return it as is.
