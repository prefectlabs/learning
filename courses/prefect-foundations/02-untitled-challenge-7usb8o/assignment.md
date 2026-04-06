---
slug: untitled-challenge-7usb8o
id: l0qkszfvenjt
type: challenge
title: Reliability & Observability
teaser: In this track, you'll learn how to transform fragile scripts into production-ready
  workflows that handle failures gracefully and provide clear visibility into what's
  happening.
notes:
- type: text
  contents: |2+
      # Why Reliability Matters

    Your Python scripts work great locally, but production is different. When APIs go down, networks slow, or databases get busy, your scripts crash—and you might not even know until hours later.

    The cost? Lost processing time, manual fixes, unreliable operations, and wasted debugging hours.

    The Solution: Prefect makes your code resilient with automatic retries, error handling, and observability—so your workflows keep running even when things go wrong.

- type: text
  contents: |-
    # Why Observability Matters

    When your workflows fail, you're flying blind. Which step broke? How long did each part take? What data was being processed? Without answers, you spend hours debugging in production.

    The Problem: No visibility into performance bottlenecks, data lineage, or where failures occur makes it nearly impossible to optimize or scale your workflows.

    The Solution: Prefect provides rich logging, execution graphs, and real-time monitoring—so you always know exactly what's happening in your workflows.
tabs:
- id: 6ayvarsnlt7h
  title: Terminal
  type: terminal
  hostname: prefect-sandbox
  cmd: /bin/bash
- id: fsg0noha3o4r
  title: "\U0001F6A7 Code Editor"
  type: code
  hostname: prefect-sandbox
  path: /root
difficulty: ""
enhanced_loading: null
---
Introduction
===

Welcome to making your workflows reliable and observable.

In this track, you'll learn how to transform fragile scripts into production workflows that handle failures and provide clear visibility.

You'll learn:

✅ **Retry strategies** that handle failures automatically

✅ **Flow and task naming** for better organization and debugging

✅ **Logging** that gives you real-time insights

✅ **Error handling** that keeps your workflows running

Let's get started.

Setup your project
===

Let's start by making a fragile API client reliable with Prefect's retry capabilities using real working APIs.

We'll use `uv` for package management.

**Install UV package manager:**

```run
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
uv --version
```

**Set up your project environment:**

First, let's check if you already have a virtual environment from the previous challenge:

```run
if [ -d ".venv" ]; then
    echo "Virtual environment already exists, activating..."
    source .venv/bin/activate
else
    echo "Creating new virtual environment..."
    uv venv && source .venv/bin/activate
    uv pip install -U prefect
fi
```

**Install additional dependencies for this challenge:**

```run
uv pip install requests pandas
```

Retries & Error Handling with Real APIs
===

**Create your API client file:**

```run
touch dev_articles_basic.py
```

Now add this code to `dev_articles_basic.py`:

```python
import requests

def fetch_dev_articles(tag: str = "python"):
    """Fetch articles from Dev.to API"""
    url = f"https://dev.to/api/articles"
    params = {"tag": tag, "per_page": 5}

    response = requests.get(url, params=params)
    return response.json()

if __name__ == "__main__":
    articles = fetch_dev_articles("prefect")
    print(f"Found {len(articles)} articles about Prefect!")
    for article in articles:
        print(f"- {article['title']}")
```

**Test the basic version:**

```run
uv run dev_articles_basic.py
```

This script will fail if the API is down or slow. Here's how to make it reliable with Prefect:

**Create the improved version:**

```run
touch dev_articles_flow.py
```

Add this code to `dev_articles_flow.py`:

```python
import requests
from prefect import flow, task

@task(retries=3, retry_delay_seconds=30)
def fetch_dev_articles(tag: str = "python", per_page: int = 5):
    """Fetch articles from Dev.to API with retry logic"""
    url = f"https://dev.to/api/articles"
    params = {"tag": tag, "per_page": per_page}

    response = requests.get(url, params=params)
    response.raise_for_status()  # This will raise an exception for HTTP errors
    return response.json()

@flow(name="dev-articles")
def dev_articles_flow(tag: str = "python"):
    """Flow to fetch and display Dev.to articles"""
    articles = fetch_dev_articles(tag)

    print(f"Found {len(articles)} articles")
    for article in articles:
        print(f"- {article['title']} by {article['user']['name']}")

    return articles

if __name__ == "__main__":
    dev_articles_flow("prefect")
```

Key concepts you just learned:
- `@task(retries=3)` - Automatically retry failed tasks up to 3 times
- `retry_delay_seconds=30` - Wait 30 seconds between retries
- `response.raise_for_status()` - Properly handle HTTP errors
- Real API integration with the Dev.to platform

Try running this and see how Prefect handles failures gracefully!

```run
uv run dev_articles_flow.py
```

Flow & Task Naming with Real ETL
===

Now let's organize your workflows with descriptive names using a real ETL pipeline with JSONPlaceholder API.

**Create your ETL pipeline file:**

```run
touch user_etl_pipeline.py
```

Add this code to `user_etl_pipeline.py`:

```python
from prefect import flow, task
import pandas as pd
import requests

def name_etl_flow():
    """Generate dynamic flow name based on parameters"""
    from prefect.context import get_run_context

    flow_run = get_run_context().flow_run
    params = flow_run.parameters
    environment = params.get("environment", "dev")

    return f"user-etl-{environment}"

@flow(flow_run_name=name_etl_flow)
def user_etl_pipeline(environment: str = "dev"):
    """ETL pipeline for user data from JSONPlaceholder API"""

    # Extract users
    users = fetch_users()

    # Transform data
    processed_users = process_user_data(users)

    # Load data
    result = save_user_data(processed_users, environment)

    return result

@task(name="fetch-users-from-api")
def fetch_users():
    """Fetch users from JSONPlaceholder API"""
    response = requests.get("https://jsonplaceholder.typicode.com/users")
    response.raise_for_status()
    return response.json()

@task(name="process-user-data")
def process_user_data(users):
    """Transform user data into a clean format"""
    processed = []
    for user in users:
        processed.append({
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "city": user["address"]["city"],
            "company": user["company"]["name"]
        })
    return processed

@task(name="save-user-data")
def save_user_data(users, destination: str):
    """Save user data to CSV"""
    df = pd.DataFrame(users)
    filename = f"users_{destination}.csv"
    df.to_csv(filename, index=False)
    return f"Saved {len(users)} users to {filename}"

if __name__ == "__main__":
    result = user_etl_pipeline("production")
    print(f"ETL Result: {result}")
```

Key concepts you just learned:
- `flow_run_name=name_etl_flow` - Dynamic flow naming using a function that reads parameters
- `get_run_context().flow_run.parameters` - Access flow parameters for dynamic naming
- `name="fetch-users-from-api"` - Descriptive task names that show in Prefect logs
- Real ETL pipeline with actual API data
- Organization in Prefect UI makes debugging much easier

Run this and see how the names appear in the Prefect logs:

```run
uv run user_etl_pipeline.py
```

You'll see the descriptive names in the execution logs - much easier to debug than generic names!

Logging & Observability with GitHub API
===

Finally, let's add comprehensive logging to monitor what's happening in your workflows using the GitHub API.

**Create your GitHub stats file:**

```run
touch github_stats_flow.py
```

Add this code to `github_stats_flow.py`:

```python
from prefect import flow, task, get_run_logger
import requests

def name_github_flow():
    """Generate dynamic flow name based on username parameter"""
    from prefect.context import get_run_context

    flow_run = get_run_context().flow_run
    params = flow_run.parameters
    username = params.get("username", "unknown")

    return f"github-stats-{username}"


@task(retries=3, retry_delay_seconds=60)
def get_github_user(username: str):
    """Fetch GitHub user information"""
    logger = get_run_logger()
    logger.info(f"Fetching GitHub user info for {username}")

    response = requests.get(f"https://api.github.com/users/{username}")
    response.raise_for_status()
    return response.json()

@task(retries=3, retry_delay_seconds=30)
def get_github_repos(username: str):
    """Fetch GitHub repositories"""
    logger = get_run_logger()
    logger.info(f"Fetching repositories for {username}")

    response = requests.get(f"https://api.github.com/users/{username}/repos")
    response.raise_for_status()
    return response.json()

@task
def calculate_repo_stats(repos):
    """Calculate repository statistics"""
    logger = get_run_logger()
    logger.info("Calculating repository statistics")

    if not repos:
        return {"total_repos": 0, "total_stars": 0, "avg_size": 0}

    total_stars = sum(repo.get("stargazers_count", 0) for repo in repos)
    total_size = sum(repo.get("size", 0) for repo in repos)

    stats = {
        "total_repos": len(repos),
        "total_stars": total_stars,
        "avg_size": total_size / len(repos) if repos else 0,
        "languages": list(set(repo.get("language", "Unknown") for repo in repos if repo.get("language")))
    }

    logger.info("Repository statistics calculated", extra=stats)
    return stats

@flow(flow_run_name=name_github_flow, log_prints=True)
def github_stats_flow(username: str = "PrefectHQ"):
    """Get GitHub statistics for a user/organization"""
    logger = get_run_logger()
    logger.info(f"Starting GitHub stats collection for {username}")

    try:
        # Get user info
        user_info = get_github_user(username)
        logger.info(f"Retrieved user info for {username}")

        # Get repositories
        repos = get_github_repos(username)
        logger.info(f"Found {len(repos)} repositories")

        # Calculate stats
        stats = calculate_repo_stats(repos)
        logger.info("Repository statistics calculated", extra={"total_repos": len(repos)})

        return {
            "username": username,
            "user_info": user_info,
            "repo_stats": stats
        }

    except Exception as e:
        logger.error(f"GitHub stats collection failed: {str(e)}", extra={"username": username})
        raise

if __name__ == "__main__":
    result = github_stats_flow("PrefectHQ")
    print(f"GitHub Stats: {result['repo_stats']}")
```

Key concepts you just learned:
- `get_run_logger()` - Get the Prefect logger for structured logging
- `logger.info()` - Log informational messages
- `logger.error()` - Log error messages with context
- `extra={"key": "value"}` - Add custom metadata to logs
- Real-time monitoring in Prefect Cloud
- Real API integration with GitHub's public API

Run this and watch the logs in real-time:

```run
uv run github_stats_flow.py
```

You'll see structured logs with detailed information about what's happening at each step!

What You've Accomplished
===

You've transformed basic Python scripts into production-ready workflows with:

✅ **Error handling** - Your workflows retry automatically when things fail

✅ **Clear organization** - Descriptive names make debugging and monitoring easier

✅ **Observability** - Logging shows what's happening

✅ **Production readiness** - Your workflows handle real-world failures

✅ **Real API integration** - Working with actual APIs like Dev.to, JSONPlaceholder, and GitHub

These concepts form the foundation of reliable, observable workflows that scale from development to production.

Next Steps
===

You're now ready for **Performance & Optimization**, where you'll learn:
- Caching strategies to avoid redundant work
- Concurrency patterns for parallel execution
- Resource optimization techniques

The journey from script to production workflow continues.

Additional Resources
===

- [Prefect Retries Documentation](https://docs.prefect.io/concepts/tasks/#retries)
- [Prefect Logging Guide](https://docs.prefect.io/concepts/logs/)
- [Prefect Flow and Task Naming](https://docs.prefect.io/concepts/flows/#flow-names)
- [Prefect Error Handling Best Practices](https://docs.prefect.io/concepts/flows/#error-handling)
- [Dev.to API Documentation](https://docs.forem.com/api/)
- [JSONPlaceholder API](https://jsonplaceholder.typicode.com/)
- [GitHub API Documentation](https://docs.github.com/en/rest)