---
title: External Links
service: FastAPI
source_urls: ["/tmp/tmp2aqkafzm/repo/docs/en/docs/external-links.md"]
scraped_at: 2026-02-17T00:28:19.430779
content_hash: c24aa7de46a2d45f76e744ce1cfc689319a59f3a00649160c48303721373876b
size_kb: 0.89
---

# External Links

**FastAPI** has a great community constantly growing.

There are many posts, articles, tools, and projects, related to **FastAPI**.

You could easily use a search engine or video platform to find many resources related to FastAPI.

/// info

Before, this page used to list links to external articles.

But now that FastAPI is the backend framework with the most GitHub stars across languages, and the most starred and used framework in Python, it no longer makes sense to attempt to list all articles written about it.

///

## GitHub Repositories

Most starred <a href="https://github.com/topics/fastapi" class="external-link" target="_blank">GitHub repositories with the topic `fastapi`</a>:

{% for repo in topic_repos %}

<a href={{repo.html_url}} target="_blank">★ {{repo.stars}} - {{repo.name}}</a> by <a href={{repo.owner_html_url}} target="_blank">@{{repo.owner_login}}</a>.

{% endfor %}
