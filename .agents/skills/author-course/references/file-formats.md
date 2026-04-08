# Instruqt File Formats Reference

## Directory Layout

```text
<track-slug>/
├── track.yml                  # Track metadata and settings
├── config.yml                 # Sandbox host definitions
├── assets/                    # Images and videos (optional)
│   ├── diagram.png
│   └── intro.mp4
├── track_scripts/             # Track-level lifecycle scripts
│   ├── setup-<hostname>       # Runs when sandbox is provisioned
│   └── cleanup-<hostname>     # Runs when sandbox is torn down
├── 01-<challenge-slug>/       # First challenge
│   ├── assignment.md          # Frontmatter config + Markdown body
│   ├── setup-<hostname>       # Runs before challenge starts
│   ├── check-<hostname>       # Validates learner completed the task
│   ├── solve-<hostname>       # Auto-solves (for skip & testing)
│   └── cleanup-<hostname>     # Runs after challenge completes
├── 02-<challenge-slug>/
│   └── ...
└── ...
```

---

## track.yml

Defines the track's metadata, ownership, and lab settings.

Use this as a repo-shaped baseline, not an exhaustive schema. When editing a pulled track, preserve existing fields that are already present even if they are not needed in a brand-new scaffold. New tracks in this repo should default to maintenance mode until they are ready to go live.

```yaml
slug: my-track-slug
# id: <assigned by Instruqt - omit for new tracks, preserve on pulled tracks>
title: My Track Title
teaser: A one-line teaser shown in track listings (max ~160 chars).
description: |-
  A longer multi-line description of the track.
  Supports Markdown. Shown on the track landing page.
icon: https://cdn.instruqt.com/assets/templates/ubuntu.png
tags:
- kubernetes
- beginner
owner: your-org-slug
developers:
- developer@example.com
maintenance: true
show_timer: true
skipping_enabled: false
idle_timeout: 300          # seconds of inactivity before warning
timelimit: 3600            # total track time limit in seconds
lab_config:
  extend_ttl: 600          # seconds a learner can extend
  sidebar_enabled: true
  feedback_recap_enabled: true
  feedback_tab_enabled: false
  loadingMessages: true
  hideStopButton: false
  theme:
    name: modern-dark       # or "original"
  default_layout: AssignmentLeft  # AssignmentRight, AssignmentBottom
  default_layout_sidebar_size: 40  # 25-100, percentage
  override_challenge_layout: false
checksum: "1234567890"
enhanced_loading: false
```

### Field notes

| Field | Required | Description |
|---|---|---|
| `slug` | Yes | URL-safe identifier, lowercase with hyphens |
| `id` | No | Assigned by Instruqt; preserve when editing an existing track |
| `title` | Yes | Human-readable track title |
| `teaser` | Yes | Short description for listings |
| `description` | Yes | Long Markdown description |
| `owner` | Yes | Instruqt org/team slug |
| `developers` | No | Email list of track developers |
| `tags` | No | Searchable tags |
| `timelimit` | No | Total track time limit (seconds) |
| `idle_timeout` | No | Inactivity timeout (seconds) |
| `skipping_enabled` | No | Allow learners to skip challenges |
| `maintenance` | No | If true, track is in maintenance mode; default new tracks to `true` and preserve the existing value on pulled tracks unless intentionally changing it |
| `checksum` | No | Usually present on pulled tracks; preserve unless you know why it should change |
| `enhanced_loading` | No | Preserve the existing value used by the track |

---

## config.yml

Defines the sandbox environment - what hosts the learner interacts with.

```yaml
version: "3"

# Container hosts
containers:
- name: container           # hostname used in scripts and tabs
  image: ubuntu:22.04       # Docker image
  shell: /bin/bash
  memory: 512               # MB

# Virtual machine hosts
virtualmachines:
- name: webserver
  image: projects/instruqt/images/ubuntu-2204
  shell: /bin/bash
  machine_type: n1-standard-2

# Website service hosts (for virtual browser tabs)
virtualbrowsers:
- name: web-app
  url: https://www.example.com

# Cloud accounts
gcp_projects:
- name: my-gcp-project
  services:
  - compute.googleapis.com
  - container.googleapis.com
  roles:
  - roles/editor

aws_accounts:
- name: my-aws-account
  managed_policies:
  - arn:aws:iam::aws:policy/AdministratorAccess

azure_subscriptions:
- name: my-azure-sub
  roles:
  - Contributor

# Sandbox secrets (available as env vars)
secrets:
- name: MY_API_KEY
```

### Common container images

| Image | Use case |
|---|---|
| `ubuntu:22.04` | General-purpose Linux |
| `gcr.io/instruqt/cloud-client` | Pre-installed cloud CLIs (gcloud, aws, az) |
| `hashicorp/terraform:latest` | Terraform labs |

---

## assignment.md

Each challenge has one `assignment.md` that combines YAML frontmatter (config) and Markdown (what the learner sees).

Use this as a baseline shape. When editing a pulled challenge, preserve existing fields like `id`, tab IDs, `difficulty`, and `enhanced_loading` instead of normalizing them away.

````yaml
---
slug: create-a-deployment
# id: <assigned by Instruqt - omit for new, preserve on pulled tracks>
type: challenge
title: Create a Kubernetes Deployment
teaser: Deploy your first application to the cluster.
notes:
- type: text
  contents: |-
    # Welcome!
    In this challenge you'll create your first Kubernetes Deployment.
- type: image
  url: ../assets/k8s-architecture.png
- type: video
  url: ../assets/intro.mp4
tabs:
- id: terminal-tab
  title: Shell
  type: terminal
  hostname: container
- id: editor-tab
  title: Code Editor
  type: code
  hostname: container
  path: /root/manifests
- id: dashboard-tab
  title: K8s Dashboard
  type: service
  hostname: container
  port: 8443
  path: /
- id: docs-tab
  title: Docs
  type: website
  url: https://kubernetes.io/docs
difficulty: ""
timelimit: 600
enhanced_loading: null
---

# Create a Kubernetes Deployment

In this challenge, you'll create a Deployment that runs an nginx web server.

## Step 1: Write the manifest

Create a file called `deployment.yaml` in the `/root/manifests` directory:

```yaml
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
```

## Step 2: Apply the manifest

Run the following command:

```text
kubectl apply -f /root/manifests/deployment.yaml
```

## Step 3: Verify

Check that both pods are running:

```text
kubectl get pods
```

You should see two pods with status `Running`.
````

### Frontmatter fields

| Field | Required | Values |
|---|---|---|
| `slug` | Yes | URL-safe challenge identifier |
| `id` | No | Assigned by Instruqt; preserve when editing an existing challenge |
| `type` | Yes | `challenge` or `quiz` |
| `title` | Yes | Challenge display title |
| `teaser` | No | Short description |
| `difficulty` | No | Usually one of `basic`, `basic-intermediate`, `intermediate`, `intermediate-advanced`, `advanced`; preserve `""` if the pulled track already uses it |
| `timelimit` | Yes | Seconds (e.g., 600 = 10 min) |
| `tabs` | Yes | Array of tab definitions (see below) |
| `notes` | No | Array of intro slides shown before challenge starts |
| `enhanced_loading` | No | Preserve the existing value used by the challenge |

Tab definitions on pulled tracks may also carry an `id`; preserve it when present.

### Tab types

**Terminal** - Opens a shell on a sandbox host:

```yaml
- title: Shell
  type: terminal
  hostname: container
  workdir: /root          # optional working directory
  cmd: "htop"             # optional command to run (locks terminal)
```

**Code editor** - Opens a file editor on a sandbox host:

```yaml
- title: Editor
  type: code
  hostname: container
  path: /root/workspace   # optional directory to open
```

**Service** - Exposes a port on a sandbox host:

```yaml
- title: App
  type: service
  hostname: container
  port: 8080
  path: /dashboard        # optional URL path
  protocol: https         # optional, default auto-detected
  new_window: false       # optional, opens in new browser tab
```

**Website** - Embeds an external URL:

```yaml
- title: Documentation
  type: website
  url: https://docs.example.com
  new_window: false       # optional
```

**Virtual browser** - Displays a website service host:

```yaml
- title: Web Console
  type: browser
  hostname: web-app       # must match a virtualbrowsers entry in config.yml
```

### Notes (intro slides)

Notes appear before a challenge starts. Types:

```yaml
notes:
- type: text
  contents: |-
    # Title
    Markdown content here.
- type: image
  url: ../assets/diagram.png
- type: video
  url: ../assets/overview.mp4
```

You should assume the user might gloss over this content, or not read all the slides if there are multiple. Use it for context, but also ensure you add the essential context to the main Markdown body that the learner sees when the challenge starts.

### Quiz challenges

For quiz/multiple-choice challenges, use `type: quiz` and add `answers`:

```yaml
---
slug: knowledge-check
type: quiz
title: Knowledge Check
teaser: Test your understanding.
answers:
- Deployment
- StatefulSet
solution:
- 0
difficulty: basic
timelimit: 300
---

Which Kubernetes resource is best for stateless applications?
```

- `answers` is an ordered list of choices.
- `solution` is a zero-indexed list of correct answer positions.

---

## Assets

Place image and video files in the `assets/` directory at the track root. Reference them using relative paths from within challenge directories:

```markdown
![Architecture](../assets/architecture.png)
```

Supported formats: PNG, JPG, GIF, SVG, MP4.
