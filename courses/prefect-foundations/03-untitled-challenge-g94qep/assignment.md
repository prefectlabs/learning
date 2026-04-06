---
slug: untitled-challenge-g94qep
id: g7cyfjyqn57z
type: challenge
title: Performance & Optimization
teaser: In this track, you'll learn how to optimize your Prefect workflows for maximum
  performance and efficiency. We'll focus on caching strategies and concurrency patterns
  that make your workflows lightning-fast.
notes:
- type: text
  contents: |-
    # Why Performance Matters

    **The Problem**: Your workflows are slow and waste resources.

    ```python
    # This is inefficient...
    def process_data():
        data1 = expensive_api_call("user1")  # 5 seconds
        data2 = expensive_api_call("user2")  # 5 seconds
        data3 = expensive_api_call("user3")  # 5 seconds
        # Total: 15 seconds, but could be much faster!
    ```

    **What happens with poor performance?**
    - Long execution times → Delayed business decisions
    - Wasted compute resources → Higher costs
    - Redundant API calls → Rate limiting and unnecessary load
    - Sequential processing → Missed opportunities for parallelization

    **The Cost**:
    - Slower time-to-insight
    - Higher infrastructure costs
    - Poor user experience
    - Missed business opportunities

    **The Solution**: Prefect provides caching and concurrency features that make your workflows blazing fast.
- type: text
  contents: |-
    # Why Optimization Matters

    **The Problem**: You don't know where your bottlenecks are.

    ```python
    # Where is the slow part?
    def mystery_pipeline():
        step1()  # Fast or slow?
        step2()  # Fast or slow?
        step3()  # Fast or slow?
    ```

    **What you need to know:**
    - Which tasks take the longest?
    - Are you making redundant API calls?
    - Could tasks run in parallel?
    - Where are the performance bottlenecks?

    **Without optimization:**
    - No visibility into performance metrics
    - Can't identify optimization opportunities
    - Wasted resources on redundant work
    - Slow workflows that don't scale

    **The Solution**: Prefect provides caching, concurrency, and monitoring tools that help you build lightning-fast workflows.
- type: text
  contents: |-
    # Why Caching Enables Smart Retries

    **The Problem**: Traditional retries waste time restarting from the beginning.

    When workflows fail, most systems restart everything from scratch, even the steps that already succeeded. This means you're paying for and waiting for work that was already completed successfully.

    **The Solution**: Prefect's caching enables retry from point of failure.

    With Prefect's intelligent caching, when a workflow fails, it automatically detects which tasks have valid cache entries and skips them during retries. Only the failed task and subsequent tasks need to be re-executed.

    **Why this matters:**
    - **Faster recovery** - Only retry what actually failed
    - **Resource efficiency** - Don't waste compute on successful steps
    - **Cost savings** - Pay only for work that needs to be redone

    Caching isn't just about performance - it's essential for building resilient workflows that recover intelligently.
tabs:
- id: 42ytcgfg8b9l
  title: "\U0001F4BB Terminal"
  type: terminal
  hostname: prefect-sandbox
  cmd: /bin/bash
- id: aii0d6ge4npb
  title: "\U0001F6A7 Code Editor"
  type: code
  hostname: prefect-sandbox
  path: /root
difficulty: ""
enhanced_loading: null
---
Introduction
===

Welcome to making your workflows fast and efficient.

In this track, you'll learn how to optimize your Prefect workflows. We'll focus on caching strategies and concurrency patterns.

You'll learn:

✅ **Caching strategies** that eliminate redundant work

✅ **Concurrency patterns** that run tasks in parallel

✅ **Resource optimization** that makes the most of your compute resources

✅ **Performance monitoring** that helps you identify bottlenecks

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
uv pip install requests aiohttp
```

This setup ensures you have all the packages needed for performance optimization examples, including `aiohttp` for async HTTP requests.


Caching & Performance
===

Let's start by eliminating redundant work with intelligent caching using real APIs.

First, let's create a script that makes expensive API calls repeatedly:

```run
touch weather_report_basic.py
```

```python
import requests
import time

def fetch_weather_data(city: str):
    """Simulate expensive weather API call"""
    print(f"Fetching weather for {city}...")
    time.sleep(2)  # Simulate API delay

    # Mock weather data
    return {
        "city": city,
        "temperature": 72,
        "humidity": 65,
        "description": "Partly cloudy"
    }

def weather_report(cities: list):
    """Generate weather report for multiple cities"""
    results = []
    for city in cities:
        # This will make redundant calls for repeated cities
        weather = fetch_weather_data(city)
        results.append(weather)
    return results

if __name__ == "__main__":
    cities = ["New York", "London", "Tokyo", "New York", "London"]  # Notice duplicates
    start_time = time.time()
    report = weather_report(cities)
    end_time = time.time()

    print(f"Report generated in {end_time - start_time:.2f} seconds")
    for weather in report:
        print(f"{weather['city']}: {weather['temperature']}°F")
```

This script wastes time on duplicate API calls. Here's how to optimize it with Prefect caching:

```run
touch weather_report_flow.py
```

```python
import requests
import time
from prefect import flow, task
from datetime import timedelta

def name_weather_flow():
    """Generate dynamic flow name"""
    from datetime import datetime
    return f"weather-report-{datetime.now().strftime('%Y-%m-%d')}"

@task(cache_key_fn=lambda city: f"weather_{city}", cache_expiration=timedelta(hours=1))
def fetch_weather_data(city: str):
    """Fetch weather data with caching"""
    print(f"Fetching weather for {city}...")
    time.sleep(2)  # Simulate API delay

    # Mock weather data
    return {
        "city": city,
        "temperature": 72,
        "humidity": 65,
        "description": "Partly cloudy"
    }

@flow(flow_run_name=name_weather_flow, log_prints=True)
def weather_report_flow(cities: list):
    """Generate weather report with intelligent caching"""
    results = []
    for city in cities:
        # Cached calls will be instant for repeated cities
        weather = fetch_weather_data(city)
        results.append(weather)
    return results

if __name__ == "__main__":
    cities = ["New York", "London", "Tokyo", "New York", "London"]  # Duplicates will use cache
    start_time = time.time()
    report = weather_report_flow(cities)
    end_time = time.time()

    print(f"Report generated in {end_time - start_time:.2f} seconds")
    for weather in report:
        print(f"{weather['city']}: {weather['temperature']}°F")
```

Key concepts:
- `cache_key_fn=lambda city: f"weather_{city}"` - Custom cache key based on input
- `cache_expiration=timedelta(hours=1)` - Cache expires after 1 hour
- Caching eliminates redundant API calls
- Performance improvement for repeated operations

Run this to see the speed improvement:

```run
uv run weather_report_flow.py
```

Now let's use a real API with caching - the JSONPlaceholder API:

```run
touch user_analytics_flow.py
```

```python
import requests
import time
from prefect import flow, task
from datetime import timedelta

def name_analytics_flow():
    """Generate dynamic flow name for user analytics"""
    from datetime import datetime
    return f"user-analytics-{datetime.now().strftime('%Y%m%d-%H%M')}"

@task(cache_key_fn=lambda user_id: f"user_{user_id}", cache_expiration=timedelta(minutes=30))
def fetch_user_details(user_id: int):
    """Fetch user details from JSONPlaceholder API with caching"""
    print(f"Fetching user {user_id} details...")

    response = requests.get(f"https://jsonplaceholder.typicode.com/users/{user_id}")
    response.raise_for_status()

    user_data = response.json()
    return {
        "id": user_data["id"],
        "name": user_data["name"],
        "email": user_data["email"],
        "company": user_data["company"]["name"]
    }

@flow(flow_run_name=name_analytics_flow, log_prints=True)
def user_analytics_flow(user_ids: list):
    """Analyze user data with intelligent caching"""
    print(f"Analyzing {len(user_ids)} users...")

    users = []
    for user_id in user_ids:
        user = fetch_user_details(user_id)
        users.append(user)

    # Calculate some analytics
    total_users = len(users)
    companies = set(user["company"] for user in users)

    return {
        "total_users": total_users,
        "unique_companies": len(companies),
        "companies": list(companies),
        "users": users
    }

if __name__ == "__main__":
    # Test with some repeated user IDs to see caching in action
    user_ids = [1, 2, 3, 1, 2, 4, 5, 1]  # Notice duplicates

    start_time = time.time()
    analytics = user_analytics_flow(user_ids)
    end_time = time.time()

    print(f"Analytics completed in {end_time - start_time:.2f} seconds")
    print(f"Total users: {analytics['total_users']}")
    print(f"Unique companies: {analytics['unique_companies']}")
```

Run this to see real API caching in action:

```run
uv run user_analytics_flow.py
```

Concurrency & Parallel Execution
===

Now let's run tasks in parallel using async patterns.

First, let's create a sequential workflow that processes multiple items:

```run
touch sequential_repo_analysis.py
```

```python
import requests
import time
from prefect import flow, task

def name_sequential_flow():
    """Generate dynamic flow name for sequential analysis"""
    from datetime import datetime
    return f"sequential-repo-analysis-{datetime.now().strftime('%H%M%S')}"

@task
def fetch_github_repo_info(owner: str, repo: str):
    """Fetch GitHub repository information"""
    print(f"Fetching {owner}/{repo}...")

    response = requests.get(f"https://api.github.com/repos/{owner}/{repo}")
    response.raise_for_status()

    repo_data = response.json()
    return {
        "name": repo_data["name"],
        "stars": repo_data["stargazers_count"],
        "forks": repo_data["forks_count"],
        "language": repo_data["language"],
        "size": repo_data["size"]
    }

@flow(flow_run_name=name_sequential_flow, log_prints=True)
def sequential_repo_analysis(repos: list):
    """Analyze repositories sequentially (slow)"""
    results = []
    for owner, repo in repos:
        repo_info = fetch_github_repo_info(owner, repo)
        results.append(repo_info)

    return results

if __name__ == "__main__":
    repos = [
        ("PrefectHQ", "prefect"),
        ("pandas-dev", "pandas"),
        ("numpy", "numpy"),
        ("scikit-learn", "scikit-learn"),
        ("matplotlib", "matplotlib")
    ]

    start_time = time.time()
    results = sequential_repo_analysis(repos)
    end_time = time.time()

    print(f"Sequential analysis completed in {end_time - start_time:.2f} seconds")
    for repo in results:
        print(f"{repo['name']}: {repo['stars']} stars, {repo['language']}")
```

This is slow because it processes repositories one by one. Here's how to make it faster with concurrency:

```run
touch concurrent_repo_analysis.py
```

```python
import asyncio
import time
import aiohttp
from prefect import flow, task

def name_concurrent_flow():
    """Generate dynamic flow name for concurrent analysis"""
    from datetime import datetime
    return f"concurrent-repo-analysis-{datetime.now().strftime('%H%M%S')}"

@task
async def fetch_github_repo_info(owner: str, repo: str):
    """Fetch GitHub repository information asynchronously"""
    print(f"Fetching {owner}/{repo}...")

    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.github.com/repos/{owner}/{repo}") as response:
            response.raise_for_status()
            repo_data = await response.json()

    return {
        "name": repo_data["name"],
        "stars": repo_data["stargazers_count"],
        "forks": repo_data["forks_count"],
        "language": repo_data["language"],
        "size": repo_data["size"]
    }

@flow(flow_run_name=name_concurrent_flow, log_prints=True)
async def concurrent_repo_analysis(repos: list):
    """Analyze repositories concurrently (fast!)"""
    # Create tasks for all repositories
    tasks = [fetch_github_repo_info(owner, repo) for owner, repo in repos]

    # Run all tasks concurrently
    results = await asyncio.gather(*tasks)

    return results

if __name__ == "__main__":
    import aiohttp

    repos = [
        ("PrefectHQ", "prefect"),
        ("pandas-dev", "pandas"),
        ("numpy", "numpy"),
        ("scikit-learn", "scikit-learn"),
        ("matplotlib", "matplotlib")
    ]

    start_time = time.time()
    results = asyncio.run(concurrent_repo_analysis(repos))
    end_time = time.time()

    print(f"Concurrent analysis completed in {end_time - start_time:.2f} seconds")
    for repo in results:
        print(f"{repo['name']}: {repo['stars']} stars, {repo['language']}")
```

Key concepts:
- `async def` - Define async functions
- `asyncio.gather(*tasks)` - Run multiple tasks concurrently
- `aiohttp` - Async HTTP client for parallel API calls
- Performance improvement through parallelization

Install aiohttp and run this to see the speed difference:

```run
uv add aiohttp
uv run concurrent_repo_analysis.py
```

Now let's combine caching AND concurrency for maximum performance:

```run
touch combined_repo_analysis.py
```

```python
import asyncio
import time
import aiohttp
from prefect import flow, task
from datetime import timedelta

def name_combined_flow():
    """Generate dynamic flow name for combined analysis"""
    from datetime import datetime
    return f"combined-repo-analysis-{datetime.now().strftime('%Y%m%d-%H%M')}"

@task(cache_key_fn=lambda owner, repo: f"repo_{owner}_{repo}", cache_expiration=timedelta(hours=2))
async def fetch_github_repo_info(owner: str, repo: str):
    """Fetch GitHub repository information with caching and async"""
    print(f"Fetching {owner}/{repo}...")

    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.github.com/repos/{owner}/{repo}") as response:
            response.raise_for_status()
            repo_data = await response.json()

    return {
        "name": repo_data["name"],
        "stars": repo_data["stargazers_count"],
        "forks": repo_data["forks_count"],
        "language": repo_data["language"],
        "size": repo_data["size"]
    }

@flow(flow_run_name=name_combined_flow, log_prints=True)
async def combined_repo_analysis(repos: list):
    """Repository analysis with caching and concurrency"""
    # Create tasks for all repositories
    tasks = [fetch_github_repo_info(owner, repo) for owner, repo in repos]

    # Run all tasks concurrently (cached ones will be instant)
    results = await asyncio.gather(*tasks)

    # Calculate some analytics
    total_stars = sum(repo["stars"] for repo in results)
    languages = set(repo["language"] for repo in results if repo["language"])

    return {
        "repos": results,
        "total_stars": total_stars,
        "languages": list(languages),
        "count": len(results)
    }

if __name__ == "__main__":
    import aiohttp

    repos = [
        ("PrefectHQ", "prefect"),
        ("pandas-dev", "pandas"),
        ("numpy", "numpy"),
        ("scikit-learn", "scikit-learn"),
        ("matplotlib", "matplotlib"),
        ("PrefectHQ", "prefect"),  # Duplicate to test caching
        ("pandas-dev", "pandas")   # Duplicate to test caching
    ]

    start_time = time.time()
    results = asyncio.run(combined_repo_analysis(repos))
    end_time = time.time()

    print(f"Combined analysis completed in {end_time - start_time:.2f} seconds")
    print(f"Total stars across all repos: {results['total_stars']}")
    print(f"Languages used: {', '.join(results['languages'])}")
    print(f"Analyzed {results['count']} repositories")
```

Run this to see caching and concurrency working together:

```run
uv run combined_repo_analysis.py
```

What You've Accomplished
===

You've transformed slow workflows into optimized systems:

✅ **Caching** - Eliminated redundant work and API calls

✅ **Parallel execution** - Tasks run concurrently

✅ **Resource optimization** - Made the most of your compute resources

✅ **Performance monitoring** - Clear visibility into execution times

✅ **Real API integration** - Applied optimization to actual APIs

These concepts form the foundation of high-performance workflows that scale efficiently.

Next Steps
===

You're now ready for **Resilience & Patterns**, where you'll learn:
- Advanced flow control and conditional logic
- Subflows for modular design
- Idempotency techniques for data consistency
- Complex error handling scenarios

The journey from script to production workflow continues.

Additional Resources
===

- [Prefect Caching Documentation](https://docs.prefect.io/concepts/tasks/#caching)
- [Prefect Async Flows Tutorial](https://docs.prefect.io/tutorials/async/)
- [Prefect Task Runners](https://docs.prefect.io/concepts/task-runners/)
- [aiohttp Documentation](https://docs.aiohttp.org/)
- [JSONPlaceholder API](https://jsonplaceholder.typicode.com/)
- [GitHub API Documentation](https://docs.github.com/en/rest)
