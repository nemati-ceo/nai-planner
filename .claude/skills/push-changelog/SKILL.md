---
name: push-changelog
description: "Push a changelog entry to the Nemati AI backend API. Use when user says push changelog, publish changelog, send changelog, create changelog entry, or log a change to the server."
disable-model-invocation: true
allowed-tools: Bash, Read, Grep
---

# Push Changelog — Send Entry to Backend API

You push changelog entries to the Nemati AI backend via a secured POST endpoint.

**RULE: Never hardcode the API key. Always read from `.env` or `.env.local`.**
**RULE: Always confirm the entry details with the user before pushing.**
**RULE: Write content as a non-technical summary — describe what changed for end users.**
**RULE: Always read `docs/changelog.md` first to build the entry from session work.**
**RULE: Always use today's date via `$(date +%Y-%m-%d)` — never hardcode a date.**
**RULE: Always check for duplicate titles before pushing — skip if already exists.**
**RULE: Always read `app_version` from `pyproject.toml` — never guess.**

---

## Workflow

### Step 1 — Read session changes
```bash
cat docs/changelog.md
```
Use the latest entries to build the changelog content.

### Step 2 — Read version
```bash
grep 'version = ' pyproject.toml | head -1
```

### Step 3 — Check for duplicates
```bash
source .env && curl -s \
  "https://nemati.ai/auth/api/v1/changelogs/changelogs/" \
  -H "Authorization: Bearer $CHANGELOG_API_KEY" \
  | python -c "
import sys, json
entries = json.load(sys.stdin)
for e in entries:
    print(f'  id={e[\"id\"]}  {e[\"date\"]}  {e[\"title\"]}')
"
```
If a title already exists, **SKIP** — do not push a duplicate.

### Step 4 — Confirm with user
Show the draft entry (title, category, content) and ask for approval before pushing.

### Step 5 — Push the entry
See **How to Push** below.

### Step 6 — Verify
Confirm the entry is live on production.

---

## Endpoint

```
POST /auth/api/v1/changelogs/changelogs/
Host: nemati.ai (production) or localhost:8000 (local)
Authorization: Bearer <CHANGELOG_API_KEY>
Content-Type: application/json
```

## Request Body (JSON)

```json
{
  "title": "nai-planner — Your title here",
  "date": "YYYY-MM-DD",
  "category": "New Feature|Improvement|Bug Fix|Security|Announcement",
  "content": "Non-technical summary of what changed.",
  "is_published": true,
  "site_names": ["nematiai"],
  "app_name": "all",
  "app_version": "0.1.0",
  "platform": "all",
  "update_available": false,
  "download_url": null
}
```

### Valid Categories

| Value | Description |
|-------|-------------|
| `New Feature` | Brand new functionality |
| `Improvement` | Enhancement to existing feature |
| `Bug Fix` | Bug fix |
| `Security` | Security patch or update |
| `Announcement` | General announcement |

---

## How to Push

```bash
TODAY=$(date +%Y-%m-%d)

cat > /tmp/changelog_entry.json << JSONEOF
{
  "title": "nai-planner — Your title here",
  "date": "$TODAY",
  "category": "New Feature",
  "content": "Non-technical summary.",
  "is_published": true,
  "site_names": ["nematiai"],
  "app_name": "all",
  "app_version": "0.1.0",
  "platform": "all",
  "update_available": false,
  "download_url": null
}
JSONEOF

source .env && EXISTING=$(curl -s \
  "https://nemati.ai/auth/api/v1/changelogs/changelogs/" \
  -H "Authorization: Bearer $CHANGELOG_API_KEY" \
  | python -c "
import sys, json
title = 'nai-planner — Your title here'
entries = json.load(sys.stdin)
print(sum(1 for e in entries if e['title'] == title))
")

if [ "$EXISTING" -gt 0 ]; then
  echo "SKIPPED — duplicate title already exists"
  rm -f /tmp/changelog_entry.json
else
  RESPONSE=$(curl -s -w "\n%{http_code}" -X POST \
    "https://nemati.ai/auth/api/v1/changelogs/changelogs/" \
    -H "Authorization: Bearer $CHANGELOG_API_KEY" \
    -H "Content-Type: application/json" \
    -d @/tmp/changelog_entry.json)

  HTTP_CODE=$(echo "$RESPONSE" | tail -1)
  BODY=$(echo "$RESPONSE" | sed '$d')

  if [ "$HTTP_CODE" = "201" ]; then
    echo "CREATED — changelog pushed successfully"
    echo "$BODY" | grep -E '"id"|"title"'
  else
    echo "FAILED (HTTP $HTTP_CODE)"
    echo "$BODY" | head -5
  fi

  rm -f /tmp/changelog_entry.json
fi
```

---

## Env Var Setup

The key must be in `.env`:
```
CHANGELOG_API_KEY=<your-key>
```

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| 401 Unauthorized | Key missing or wrong | Check `CHANGELOG_API_KEY` in env |
| 400 Invalid category | Typo in category value | Use exact values from the table above |
| 500 Internal Server Error | DB error | Check server logs |
