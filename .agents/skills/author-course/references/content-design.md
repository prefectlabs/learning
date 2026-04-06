# Content Design & Lifecycle Scripts Reference

## The Tell / Show / Do Method

Effective Instruqt tracks serve three learner types:

- **Listeners** learn from explanations -> use *Tell* (text descriptions, context)
- **Watchers** learn from demonstrations -> use *Show* (diagrams, screenshots, videos)
- **Doers** learn from practice -> use *Do* (hands-on tasks with check scripts)

Every challenge should blend all three. A strong pattern:

1. **Notes** (before the challenge) - Tell and Show. Use intro slides with text explanations, architecture diagrams, or short videos.
2. **Assignment body** - Tell and Do. Start with a brief explanation of what the learner will do and why, then give step-by-step hands-on instructions.
3. **Tabs** - Do. Give learners terminals, editors, and dashboards to complete the task.
4. **Check scripts** - Instant feedback to confirm the learner succeeded.

## Writing Good Assignments

### Structure each challenge's Markdown body like this:

````markdown
# <Action Verb> + <Object>

<1-5 sentences explaining what the learner will do and why it matters.>

## Step 1: <Short description>

<Brief explanation of this step.>

```<language>
<command or code the learner should run/write>
```

## Step 2: <Short description>

<Brief explanation.>

```<language>
<command or code>
```

## Verify

<Tell the learner how to confirm their work before clicking Check.>
````

### Tips

- **Lead with action.** Challenge titles should start with a verb: "Deploy an Application", "Configure Networking", "Debug the Service".
- **Keep challenges focused.** Each challenge should teach one concept or complete one task. 5-15 minutes is the sweet spot.
- **Be explicit.** Provide exact commands and file paths. Learners should not have to guess.
- **Use code fences.** Wrap all commands and file contents in triple backticks with language hints.
- **Add a Verify section.** Before the learner clicks Check, tell them what a successful result looks like (e.g., "You should see two pods with status Running").
- **Use notes for context.** Heavy conceptual explanation belongs in notes (shown before the challenge), not in the assignment body. Keep the body action-oriented.
- **Include images.** Architecture diagrams and UI screenshots make instructions much clearer. Reference them from `../assets/`.
- **Progressive complexity.** Start with basic challenges and build. Early challenges should give exact commands; later ones can ask learners to figure things out with hints.
- **Time limits.** Set generous time limits. A challenge you can complete in 5 minutes should have a 20-minute limit (`timelimit: 1200`) to account for reading and mistakes.

## Track Design Patterns

These are general guidelines, not hard rules. The right design depends on the content and audience.

### Introductory track (beginner audience)
- 4-6 challenges, basic difficulty
- Every command spelled out
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

# Install required software
apt-get update
apt-get install -y curl git jq

# Clone example repo
git clone https://github.com/example/repo.git /root/repo

# Pre-pull container images (speeds up learner experience)
docker pull nginx:1.24
```

The bootstrap wait is important - it ensures the host is fully initialized before your setup script modifies the environment. Always include it in track-level setup scripts.

### Script template: challenge setup

```bash
#!/bin/bash
set -euxo pipefail

# Create files the learner will need for this challenge
mkdir -p /root/workspace
cat > /root/workspace/starter.yaml << 'EOF'
apiVersion: v1
kind: ConfigMap
metadata:
  name: example
data:
  key: value
EOF
```

Challenge setup scripts don't usually need the bootstrap wait because the track setup already completed.

### Script template: challenge check

```bash
#!/bin/bash
set -euxo pipefail

# Check that the learner created the expected deployment
if ! kubectl get deployment nginx -o jsonpath='{.spec.replicas}' 2>/dev/null | grep -q "2"; then
  fail-message "The nginx deployment should have 2 replicas. Check your deployment manifest and try again."
  exit 1
fi

# Check that pods are running
RUNNING=$(kubectl get pods -l app=nginx --field-selector=status.phase=Running --no-headers 2>/dev/null | wc -l)
if [ "$RUNNING" -lt 2 ]; then
  fail-message "Expected 2 running nginx pods, but found $RUNNING. Wait a moment and try again, or check your deployment."
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

# Automate the correct solution (used for skip and testing)
cat > /root/manifests/deployment.yaml << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
spec:
  replicas: 2
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.24
        ports:
        - containerPort: 80
EOF

kubectl apply -f /root/manifests/deployment.yaml
kubectl rollout status deployment/nginx --timeout=60s
```

Solve scripts must produce the exact state that the check script validates. They're essential for `instruqt track test` to work.

### Script template: challenge cleanup

```bash
#!/bin/bash
set -euxo pipefail

# Clean up resources from this challenge before the next one starts
kubectl delete deployment nginx --ignore-not-found
rm -f /root/manifests/deployment.yaml
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
