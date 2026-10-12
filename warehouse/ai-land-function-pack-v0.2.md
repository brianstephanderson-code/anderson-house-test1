# AI LAND Function Pack v0.2

Status: GREEN

Validated live functions:
- cast_search -> CLOUDFLARE_AI_CASTS
- search_web_public -> SEARCH_WEB_PUBLIC
- fetch_text -> FETCH_TEXT
- read_text_links -> READ_TEXT_LINKS

Live replay run:
- workflow: .github/workflows/ai-land-function-pack-v0.2.yml
- run id: 38249750795
- all matrix jobs: success
- pack summary gate: success

Validated chain:
QUESTION
-> CAST
-> SEARCH
-> READ
-> EXTRACT LINKS
-> RETURN
-> VERIFY
-> DONE
