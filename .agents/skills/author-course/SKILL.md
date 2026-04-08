---
name: author-course
description: >
  Author self-paced hands-on training content for the Instruqt platform. This skill covers creating new tracks and challenges from scratch, editing pulled tracks stored locally in a "courses" folder, writing assignment markdown, configuring sandboxes, and authoring setup/check/solve/cleanup lifecycle scripts.
allowed-tools: Bash("instruqt auth login:*") Bash("instruqt track create:*") Bash("instruqt track pull:*") Bash("instruqt track validate:*") Bash("instruqt track test:*") Bash("instruqt track push:*") Bash("instruqt track open:*") Bash("instruqt challenge create:*") Bash("instruqt note create:*")
---

# Course Authoring

Create and edit self-paced, hands-on training content for Instruqt. Tracks are stored locally in a `courses/` folder and managed via the Instruqt CLI.

## When to use this skill

Use this skill whenever the user mentions Instruqt, hands-on labs, interactive training tracks, lab challenges, sandbox environments, or wants to create technical training content with check scripts. Also trigger when the user references track.yml, config.yml, assignment.md, lifecycle scripts, or the Instruqt CLI (instruqt track pull/push/create).

## Assumed Workflow

The user works locally with the Instruqt CLI. Tracks live under a `courses/` directory:

```text
courses/
├── my-first-track/
│   ├── track.yml
│   ├── config.yml
│   ├── assets/              # optional images/videos
│   ├── track_scripts/
│   │   ├── setup-<hostname>
│   │   └── cleanup-<hostname>
│   ├── 01-first-challenge/
│   │   ├── assignment.md
│   │   ├── setup-<hostname>
│   │   ├── check-<hostname>
│   │   ├── solve-<hostname>
│   │   └── cleanup-<hostname>
│   └── 02-second-challenge/
│       ├── assignment.md
│       └── ...
└── another-track/
    └── ...
```

CLI cheat-sheet:
- `instruqt auth login` - authenticate when the CLI session is missing or expired
- `instruqt track pull <org>/<slug>` - download a track into the current directory
- `instruqt track push` - upload local changes
- `instruqt track create --title "Title"` - scaffold a new track
- `instruqt challenge create --title "Title"` - add a challenge to the current track
- `instruqt note create --challenge <challenge-slug> --type text` - add a text note to a challenge
- `instruqt track test` - run lifecycle scripts end-to-end
- `instruqt track validate` - check file structure validity
- `instruqt track open` - inspect the published track in a browser

## How to Author Content

When the user asks you to create or edit Instruqt content, read the appropriate reference files in this skill's `references/` directory before writing any files:

- `references/file-formats.md` - Exact YAML schemas for `track.yml`, `config.yml`, and `assignment.md` frontmatter, plus tab type syntax.
- `references/content-design.md` - Pedagogy guidelines (Tell/Show/Do), challenge writing tips, and lifecycle script patterns.

## Step-by-Step Process

1. **Explore first** - If the request is about an existing track, inspect `track.yml`, `config.yml`, challenge frontmatter, and script filenames before asking questions. Infer hostnames, audience, challenge count, and existing conventions from local files whenever possible.
2. **Clarify only what is missing** - Ask follow-up questions only for product intent or decisions that are not discoverable from the local track.
3. **Authenticate if needed** - If an Instruqt CLI command fails with an auth or token-refresh error, run `instruqt auth login` and retry.
4. **Read references** - Before generating or editing files, read `references/file-formats.md` and `references/content-design.md`.
5. **Generate or update the track** - Create or edit files under `courses/<track-slug>/`. Start with `track.yml` and `config.yml`, then update each challenge directory with its `assignment.md` and lifecycle scripts. For brand-new tracks, set `maintenance: true` in `track.yml` unless the user explicitly asks for a live/published-ready track, and include `draft` in `tags:` by default until the course is intentionally retagged for publication.
6. **Write assignment content** - Each `assignment.md` has YAML frontmatter (separated by `---`) followed by Markdown. Apply the Tell/Show/Do method: explain concepts first, then give the learner hands-on tasks.
7. **Write lifecycle scripts** - Every script in this repo should start with `#!/bin/bash` and `set -euxo pipefail`. Track setup scripts should wait for bootstrap. Check scripts should validate the learner's work and exit non-zero on failure. Solve scripts should automate the correct solution.
8. **Validate and test** - Run `instruqt track validate` and `instruqt track test` before publishing.
9. **Present the result** - Summarize the files created or changed and call out anything the user should review.

## Key Rules

- Challenge directories are numbered: `01-slug/`, `02-slug/`, etc.
- Hostnames in script filenames must match hostnames defined in `config.yml`.
- `assignment.md` uses `---` fenced YAML frontmatter at the top; the Markdown body follows.
- The `type` field in assignment frontmatter is always `challenge` (or `quiz` for quiz challenges).
- Time limits are in seconds (e.g. `timelimit: 600` = 10 minutes).
- Difficulty values: `basic`, `basic-intermediate`, `intermediate`, `intermediate-advanced`, `advanced`.
- Assets go in `assets/` at the track root; reference them with relative paths from challenge directories.
- YAML indentation uses spaces only, never tabs.
- The `owner` field in `track.yml` must match the user's Instruqt team/org slug.
- Leave `id` fields empty or omit them for new content; preserve IDs that already exist on pulled tracks.
- New tracks should default to `maintenance: true`; preserve the existing `maintenance` value on pulled tracks unless the user asks to change it.
- New tracks should include `draft` in `tags:` by default; keep other topical tags as needed and remove `draft` only when the track is ready for publication.
- When editing pulled tracks, preserve existing metadata fields and tab IDs unless you are intentionally changing them.
