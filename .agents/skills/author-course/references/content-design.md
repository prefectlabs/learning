# Content Design & Lifecycle Scripts Reference

## The Tell / Show / Do Method

Effective Instruqt tracks serve three learner types:

- **Listeners** learn from explanations -> use *Tell* (text descriptions, context)
- **Watchers** learn from demonstrations -> use *Show* (diagrams, screenshots, videos)
- **Doers** learn from practice -> use *Do* (hands-on tasks with check scripts)

Every challenge should blend all three. A strong pattern:

1. **Notes** (before the challenge) - Tell and Show. Start with a short prose introduction that explains what is happening, why it matters, and what the learner should notice before they begin. Use diagrams, screenshots, or short videos after that context when they help.
2. **Assignment body** - Tell and Do. Start with a brief, prose-rich opening paragraph or two that explains what the learner will do and why, then give step-by-step hands-on instructions. Each step should have 1-3 sentences of explanation before the code block — the prose is where the teaching happens, the code block is where the doing happens. Both are required.
3. **Tabs** - Do. Give learners terminals, editors, and dashboards to complete the task.
4. **Check scripts** - Instant feedback to confirm the learner succeeded.

## Writing Good Assignments

### Structure each challenge's Markdown body like this:

````markdown
# <Action Verb> + <Object>

<1-2 short paragraphs explaining what the learner will do, why it matters, and
how it connects to what they have seen so far. This is the teaching frame — do
not skip it even when the task feels obvious.>

## Step 1: <Short description>

<1-3 sentences explaining what this command or file does, why the learner is
doing it now, and anything non-obvious about what will happen. A step that is
just a heading and a code fence is too thin — the explanation is the teaching.>

```<language>
<command or code the learner should run/write>
```

## Step 2: <Short description>

<1-3 sentences, same pattern. Connect this step to the previous one if the
relationship is not obvious.>

```<language>
<command or code>
```

## Verify

<Tell the learner what success looks like — expected output, visible state, or a
command they can run. Be concrete: "You should see two pods with status Running"
is better than "Verify that it worked.">
````

### Tips

- **Lead with action.** Challenge titles should start with a verb: "Deploy an Application", "Configure Networking", "Debug the Service".
- **Keep challenges focused.** Each challenge should teach one concept or complete one task. 5-15 minutes is the sweet spot.
- **Be explicit.** Provide exact commands and file paths. Learners should not have to guess.
- **Use code fences.** Wrap all commands and file contents in triple backticks with language hints.
- **Add a Verify section.** Before the learner clicks Check, tell them what a successful result looks like (e.g., "You should see two pods with status Running").
- **Use notes for background, not as a substitute for in-body explanation.** Notes are for context the learner needs before they start — background concepts, architecture overviews, or "why this matters." The assignment body still needs its own opening paragraph and per-step explanations. If a step has no prose before its code fence, the body is too thin regardless of what the notes cover.
- **Include images.** Architecture diagrams and UI screenshots make instructions much clearer. Reference them from `../assets/`.
- **Progressive complexity.** Start with the smallest working code example and build from there. Early challenges should give exact commands with few moving parts; later ones can ask learners to figure things out with hints. This applies to the *code and task scope* — not to the prose. Early challenges often need *more* explanation, not less, because the learner has less context.
- **Time limits.** Set generous time limits. A challenge you can complete in 5 minutes should have a 20-minute limit (`timelimit: 1200`) to account for reading and mistakes.

## Track Design Patterns

These are general guidelines, not hard rules. The right design depends on the content and audience.

### Introductory track (beginner audience)
- 4-6 challenges, basic difficulty
- Every command spelled out
- Smallest working examples first
- Heavy use of notes with diagrams
- Check scripts validate exact outcomes

### Workshop track (intermediate audience)
- 6-10 challenges, mix of difficulties
- Early challenges are guided; later ones give goals with hints
- Includes a "cleanup" or "destroy" challenge at the end

### Certification/assessment track
- Mix of challenge and quiz types
- Quiz challenges between hands-on sections
- Stricter check scripts, no solve scripts

---

## Lifecycle Scripts

All lifecycle scripts are bash files that run on sandbox hosts. They follow a `<action>-<hostname>` naming convention.

### Track-level scripts (in `track_scripts/`)

| Script | When it runs | Purpose |
|---|---|---|
| `setup-<hostname>` | When sandbox is first created | Install software, clone repos, pre-configure the environment |
| `cleanup-<hostname>` | When sandbox is destroyed | Clean up external resources (API calls, cloud resources) |

### Challenge-level scripts (in each challenge directory)

| Script | When it runs | Purpose |
|---|---|---|
| `setup-<hostname>` | Before the challenge starts | Prepare state for this specific challenge |
| `check-<hostname>` | When learner clicks "Check" | Validate the learner's work; exit 0 = pass, exit 1 = fail |
| `solve-<hostname>` | When learner clicks "Skip" or during `instruqt track test` | Automate the correct solution |
| `cleanup-<hostname>` | After the challenge completes | Reset state before the next challenge |

### Script template: track setup

```bash
#!/bin/bash
set -euxo pipefail

# Wait for Instruqt host bootstrap to finish
until [ -f /opt/instruqt/bootstrap/host-bootstrap-completed ]; do
  sleep 1
done

# Create a simple starting point for the learner
mkdir -p /root/workspace
printf 'Use this folder for the lab.\n' > /root/workspace/README.txt
```

The bootstrap wait is important - it ensures the host is fully initialized before your setup script modifies the environment. Always include it in track-level setup scripts.

### Script template: track setup with assets

```bash
#!/bin/bash
set -euxo pipefail

# Wait for Instruqt host bootstrap to finish
until [ -f /opt/instruqt/bootstrap/host-bootstrap-completed ]; do
  sleep 1
done

mkdir -p /root/workspace
curl -LO "https://play.instruqt.com/assets/tracks/${INSTRUQT_TRACK_ID}/${ASSET_HASH}/assets/starter-files.tar.gz"
tar -xzf starter-files.tar.gz -C /root/workspace
```

Use this pattern when a track-level setup script needs starter files from `assets/`. If you need several files, bundle them into a `.tar.gz` first and unpack them here.

If a course uses generated assets, keep the source files in `asset-sources/` and let its `build-assets` script publish the tarball or other output into `assets/` before this setup step runs.

When a bootstrap bundle is only needed by setup scripts, hide the asset reference in a Markdown comment so the file uploads without adding learner-facing noise.

### Script template: challenge setup

```bash
#!/bin/bash
set -euxo pipefail

mkdir -p /root/workspace
printf 'change me\n' > /root/workspace/message.txt
```

Challenge setup scripts don't usually need the bootstrap wait because the track setup already completed.

### Script template: challenge check

```bash
#!/bin/bash
set -euxo pipefail

if ! grep -qx "done" /root/workspace/message.txt 2>/dev/null; then
  fail-message "Put only done on the first line of /root/workspace/message.txt."
  exit 1
fi
```

Key rules for check scripts:
- Exit 0 means the check passed. Exit 1 (or any non-zero) means it failed.
- Use `fail-message "text"` to show a helpful error to the learner. This is an Instruqt built-in.
- Check the *outcome*, not the exact method. If there are multiple valid approaches, validate the end state.
- Be specific in fail messages - tell the learner what's wrong and hint at how to fix it.

### Script template: challenge solve

```bash
#!/bin/bash
set -euxo pipefail

printf 'done\n' > /root/workspace/message.txt
```

Solve scripts must produce the exact state that the check script validates. They're essential for `instruqt track test` to work.

### Script template: challenge cleanup

```bash
#!/bin/bash
set -euxo pipefail

rm -f /root/workspace/message.txt /root/workspace/README.txt
```

---

## Environment Variables in Scripts

Instruqt provides several environment variables to scripts:

| Variable | Description |
|---|---|
| `INSTRUQT_PARTICIPANT_ID` | Unique ID for the current learner session |
| `INSTRUQT_TRACK_ID` | ID of the current track |
| `INSTRUQT_TRACK_SLUG` | Slug of the current track |

Secrets defined in `config.yml` are also available as environment variables.

## Common Pitfalls

- **Forgetting `set -euxo pipefail`** - Without this, scripts may silently fail and leave the sandbox in a broken state.
- **Missing bootstrap wait** - Track setup scripts that modify `/root/.bashrc` or install packages before bootstrap completes will break.
- **Hostname mismatch** - Script filenames (e.g., `check-container`) must use the exact hostname from `config.yml`. If your host is called `webserver`, the script must be `check-webserver`.
- **Incorrect assignment.md format** - The `---` YAML frontmatter fences are mandatory. The first line must be `---` and the frontmatter must end with `---` followed by the Markdown body.
- **Tabs referencing non-existent hosts** - Every `hostname` in a tab definition must exist in `config.yml`.
- **Overly strict checks** - Check the result, not the method. Don't verify that a learner used a specific command; verify that the expected resource/file/state exists.
