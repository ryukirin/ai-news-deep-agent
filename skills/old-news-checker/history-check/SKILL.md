---
name: history-check
description: Use when checking whether the current list of news articles contains past news from /history/news_history.txt. Removes past news from the current list.
---

# history-check

## Steps

1. Read the list of past news from /history/news_history.txt.
2. Compare the articles in the current list with the past news and check for duplicate or similar news content.
3. If an article in the current list duplicates any past news item, remove it from the list.
4. Return the structured list of news articles with no past news.

## Examples

Past news: Company A released new product X, expected to launch next month.
News 1: Company A's X is planned to launch next month.
News 2: Company A's X.
All three cover the same story and count as duplicates.

News 4: Features and functions of Company A's new product X.
Compare this article with the past news. If the content is highly similar and the focus is the same, it also counts as a duplicate.

## Edge cases

- If the current list is empty, return an empty list.
- If /history/news_history.txt does not exist or is empty, return the current list.
- If every article in the current list duplicates past news, return an empty list.
