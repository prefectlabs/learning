---
slug: adaptive-workflow-challenge-xsygn8
id: jelr21pn5hlr
type: challenge
title: Adaptive Workflow Configuration
teaser: Build intelligent workflows that adapt configuration based on runtime data.
  Learn dynamic task configuration using with_options() and decorator parameters to
  optimize retry policies, timeouts, and processing modes automatically.
notes:
- type: text
  contents: |2-
     # The Problem: Static Configuration Wastes Resources

      Traditional workflows use the same configuration for everything. Small datasets get unnecessary heavy retries,
      large datasets fail with insufficient timeouts, and you're always guessing at the right settings. This leads to
      wasted compute resources, failed processes, and maintenance headaches when requirements change.
- type: text
  contents: |2-
      # The Solution: Two Approaches to Dynamic Configuration

      Prefect offers direct decorator parameters for static configuration with monitoring hooks, and the runtime
      with_options() method for adapting based on data characteristics. You can inspect your data first, then
      dynamically configure retry policies, timeouts, and processing modes based on actual conditions like dataset size
       or API complexity.
- type: text
  contents: |2-
     # Real-World Impact: Intelligent Workflows

      Your workflows now inspect data first, then configure themselves optimally. Small datasets get fast processing
      with minimal retries, while large datasets receive robust handling with extended timeouts. Failed attempts
      trigger automatic fallback strategies. The result is cost savings from right-sized resources, higher reliability
      with appropriate retry policies, and better performance through adaptive optimization.
tabs:
- id: gmmeji89xmsk
  title: Terminal
  type: terminal
  hostname: prefect-sandbox
  cmd: /bin/bash
- id: ohbebkte80nw
  title: "\U0001F6A7 Code Editor"
  type: code
  hostname: prefect-sandbox
  path: /root
difficulty: ""
enhanced_loading: null
---
Introduction
===

Let's start by eliminating rigid configurations with intelligent dynamic task and flow configuration using both `with_options()` and direct decorator parameters.

**Why This Matters:**
Static configurations force all your workflows to use the same retry counts, timeouts, and processing approaches regardless of the data they're handling. This leads to:
- Wasted resources on small datasets that don't need heavy retries
- Failed processes on large datasets that need more robust handling
- Poor user experience due to inappropriate timeout settings
- Maintenance headaches when requirements change

Dynamic configuration lets your workflows adapt intelligently to real conditions.

**What You'll Learn:**
- Dynamic task configuration using `with_options()`
- Direct decorator parameters for flows and tasks
- Flow decorator options: `retries`, `timeout_seconds`, `on_failure`, `on_completion`
- Runtime decision-making based on data characteristics
- When to use each approach and combining both strategies
- Fallback and error recovery patterns

Setting up your Development Environment
===
Before we begin, let's ensure `uv` and Prefect are instaled.  We'll use `uv` for package management.

**Install UV package manager:**

```run
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
uv --version
```

**Set up your project and install the `prefect` SDK**

```run
uv venv && source .venv/bin/activate
uv pip install -U prefect
```


Hands-On Exercise
===

Transform a rigid, one-size-fits-all workflow into an intelligent, adaptive system.

First, let's create a script that shows the limitations of static configuration:

```python
import requests
import time
from prefect import flow, task

def fetch_weather_data(city: str, processing_level: str):
    """Simulate different processing requirements"""
    print(f"Processing {city} with {processing_level} level...")

    if processing_level == "thorough":
        time.sleep(3)  # Slow processing
    elif processing_level == "fast":
        time.sleep(0.5)  # Quick processing
    else:
        time.sleep(1)  # Standard processing

    # Mock weather data
    return {
        "city": city,
        "temperature": 72,
        "humidity": 65,
        "description": "Partly cloudy"
    }

def static_weather_pipeline(cities: list):
    """Inefficient static pipeline"""
    results = []
    for city in cities:
        # Always uses the same processing approach - not adaptive!
        weather = fetch_weather_data(city, "standard")
        results.append(weather)
    return results

if __name__ == "__main__":
    cities = ["New York", "London", "Tokyo"]
    start_time = time.time()
    report = static_weather_pipeline(cities)
    end_time = time.time()

    print(f"Static pipeline completed in {end_time - start_time:.2f} seconds")
```

This script wastes resources with one-size-fits-all configuration. Notice how every city gets "standard" processing regardless of its complexity or data requirements.

Let's transform this into an intelligent system that adapts its behavior based on what it discovers about the data:

```python
import requests
import time
from datetime import timedelta
from prefect import flow, task, get_run_logger

@task
def fetch_api_data(endpoint: str):
    """Fetch data from JSONPlaceholder API"""
    logger = get_run_logger()
    logger.info(f"Fetching data from {endpoint}")

    response = requests.get(f"https://jsonplaceholder.typicode.com/{endpoint}")
    response.raise_for_status()
    return response.json()

@task
def process_data(data, processing_mode: str = "standard"):
    """Process data with configurable behavior"""
    logger = get_run_logger()
    logger.info(f"Processing {len(data)} items in {processing_mode} mode")

    # Simulate different processing based on mode
    if processing_mode == "thorough":
        time.sleep(2)  # Thorough processing
    elif processing_mode == "fast":
        time.sleep(0.5)  # Quick processing
    else:
        time.sleep(1)  # Standard processing

    # Simulate failures for large datasets in fast mode
    if len(data) > 50 and processing_mode == "fast":
        raise Exception("Fast processing failed on large dataset")

    return [{
        "id": item.get("id", i),
        "title": item.get("title", item.get("name", f"Item {i}")),
        "processed_mode": processing_mode
    } for i, item in enumerate(data[:5])]  # Process first 5 items

@flow(name="adaptive-processing-{data_type}")
def adaptive_processing_flow(data_type: str = "posts"):
    """Pipeline that adapts configuration based on data characteristics"""
    logger = get_run_logger()
    logger.info(f"Starting adaptive processing for {data_type}")

    # Fetch data first to understand characteristics
    raw_data = fetch_api_data(data_type)
    data_size = len(raw_data)

    logger.info(f"Fetched {data_size} items, determining optimal configuration...")

    # Adapt configuration based on data size
    if data_size > 50:
        # Large dataset: high reliability configuration
        retry_config = {"retries": 5, "retry_delay_seconds": 30}
        processing_mode = "thorough"
        logger.info("Large dataset: using high-reliability configuration")
    elif data_size > 10:
        # Medium dataset: balanced configuration
        retry_config = {"retries": 3, "retry_delay_seconds": 15}
        processing_mode = "standard"
        logger.info("Medium dataset: using balanced configuration")
    else:
        # Small dataset: fast configuration
        retry_config = {"retries": 1, "retry_delay_seconds": 5}
        processing_mode = "fast"
        logger.info("Small dataset: using fast configuration")

    # Dynamically configure the processing task
    adaptive_task = process_data.with_options(**retry_config)

    # Execute with adaptive configuration
    try:
        result = adaptive_task(raw_data, processing_mode)
        logger.info(f"Successfully processed {len(result)} items")
        return {
            "data_type": data_type,
            "original_count": data_size,
            "processed_count": len(result),
            "processing_mode": processing_mode,
            "retry_config": retry_config,
            "data": result
        }
    except Exception as e:
        logger.error(f"Processing failed: {str(e)}")
        # Fallback with conservative settings
        logger.info("Attempting fallback with conservative settings...")

        fallback_task = process_data.with_options(retries=2, retry_delay_seconds=10)
        result = fallback_task(raw_data, "standard")

        return {
            "data_type": data_type,
            "original_count": data_size,
            "processed_count": len(result),
            "processing_mode": "standard",
            "retry_config": {"retries": 2, "retry_delay_seconds": 10},
            "fallback_used": True,
            "data": result
        }

if __name__ == "__main__":
    # Test with different data types (different sizes)
    data_types = ["posts", "users", "comments"]  # ~100, ~10, ~500 items

    for data_type in data_types:
        print(f"\n--- Processing {data_type} ---")
        result = adaptive_processing_flow(data_type)
        print(f"Result: {result['processed_count']} items processed in {result['processing_mode']} mode")
        print(f"Retry configuration: {result['retry_config']}")
```

**Key concepts you just learned:**
- `task.with_options(retries=5, retry_delay_seconds=30)` - Dynamic task configuration at runtime
- **Data-driven decisions** - Let the actual data characteristics determine optimal configuration
- **Fallback strategies** - Graceful degradation when primary configuration fails
- **Runtime optimization** - No more guessing what configuration will work best

Try running this to see adaptive configuration in action:

```run
python3 adaptive_processing_flow.py
```

Now let's explore the **two approaches** to configuration and when to use each:

Approach 1: Direct Decorator Parameters
===

You can configure flows and tasks directly in their decorators:

```python
import requests
import time
from datetime import timedelta
from prefect import flow, task, get_run_logger

@task(retries=3, retry_delay_seconds=10, timeout_seconds=30)
def fetch_user_data(user_id: int):
    """Fetch user data with direct decorator configuration"""
    logger = get_run_logger()
    logger.info(f"Fetching data for user {user_id}")

    response = requests.get(f"https://jsonplaceholder.typicode.com/users/{user_id}")
    response.raise_for_status()
    return response.json()

@flow(
    name="user-analysis-{user_id}",
    retries=2,
    timeout_seconds=120,
    on_failure=lambda flow, flow_run, state: print(f"Flow {flow_run.name} failed: {state.message}"),
    on_completion=lambda flow, flow_run, state: print(f"Flow {flow_run.name} completed: {state.type}")
)
def analyze_user_flow(user_id: int = 1):
    """Flow with direct decorator configuration and hooks"""
    logger = get_run_logger()
    logger.info(f"Starting user analysis for user {user_id}")

    user_data = fetch_user_data(user_id)

    # Simulate analysis
    time.sleep(1)

    analysis = {
        "user_id": user_data["id"],
        "name": user_data["name"],
        "email": user_data["email"],
        "company": user_data["company"]["name"],
        "analysis_timestamp": time.time()
    }

    logger.info(f"Analysis complete for {user_data['name']}")
    return analysis

if __name__ == "__main__":
    result = analyze_user_flow(1)
    print(f"Analysis result: {result}")
```

Approach 2: Dynamic Configuration with `with_options()`
===

For runtime configuration based on conditions:

```python
import requests
import time
from datetime import timedelta
from prefect import flow, task, get_run_logger

@task
def fetch_data(endpoint: str):
    """Base task without fixed configuration"""
    logger = get_run_logger()
    logger.info(f"Fetching from {endpoint}")

    response = requests.get(f"https://jsonplaceholder.typicode.com/{endpoint}")
    response.raise_for_status()
    return response.json()

@task
def process_data(data, processing_mode: str = "standard"):
    """Base processing task"""
    logger = get_run_logger()
    logger.info(f"Processing {len(data)} items in {processing_mode} mode")

    if processing_mode == "thorough":
        time.sleep(2)
    elif processing_mode == "fast":
        time.sleep(0.5)
    else:
        time.sleep(1)

    return [{"id": item.get("id", i), "title": item.get("title", f"Item {i}")}
            for i, item in enumerate(data[:3])]

@flow(name="adaptive-data-processing-{endpoint}")
def adaptive_processing_flow(endpoint: str = "posts"):
    """Flow that dynamically configures tasks based on data characteristics"""
    logger = get_run_logger()

    # Fetch data to understand characteristics
    raw_data = fetch_data(endpoint)
    data_size = len(raw_data)

    logger.info(f"Data size: {data_size} items")

    # Choose configuration based on data size
    if data_size > 50:
        # Large dataset: high reliability
        task_config = {"retries": 5, "retry_delay_seconds": 30, "timeout_seconds": 60}
        processing_mode = "thorough"
        flow_config = {"retries": 3, "timeout_seconds": 300}
    elif data_size > 10:
        # Medium dataset: balanced
        task_config = {"retries": 3, "retry_delay_seconds": 15, "timeout_seconds": 30}
        processing_mode = "standard"
        flow_config = {"retries": 2, "timeout_seconds": 180}
    else:
        # Small dataset: fast
        task_config = {"retries": 1, "retry_delay_seconds": 5, "timeout_seconds": 15}
        processing_mode = "fast"
        flow_config = {"retries": 1, "timeout_seconds": 60}

    # Create dynamically configured tasks
    configured_fetch = fetch_data.with_options(**task_config)
    configured_process = process_data.with_options(**task_config)

    # Execute with dynamic configuration
    try:
        data = configured_fetch(endpoint)
        result = configured_process(data, processing_mode)

        logger.info(f"Successfully processed {len(result)} items")
        return {
            "endpoint": endpoint,
            "original_count": data_size,
            "processed_count": len(result),
            "processing_mode": processing_mode,
            "config_used": task_config
        }
    except Exception as e:
        logger.error(f"Processing failed: {str(e)}")
        # Fallback with conservative settings
        fallback_config = {"retries": 2, "retry_delay_seconds": 10, "timeout_seconds": 30}
        fallback_task = process_data.with_options(**fallback_config)

        result = fallback_task(raw_data, "standard")
        return {
            "endpoint": endpoint,
            "original_count": data_size,
            "processed_count": len(result),
            "processing_mode": "standard",
            "fallback_used": True,
            "config_used": fallback_config
        }

if __name__ == "__main__":
    # Test with different endpoints
    endpoints = ["posts", "users", "comments"]

    for endpoint in endpoints:
        print(f"\n--- Processing {endpoint} ---")
        result = adaptive_processing_flow(endpoint)
        print(f"Result: {result['processed_count']} items processed")
        print(f"Mode: {result['processing_mode']}")
        print(f"Config: {result['config_used']}")
```

When to Use Each Approach
===

**Use Direct Decorator Parameters When:**
- Configuration is known at development time
- You want consistent behavior across all runs
- You need hooks (`on_failure`, `on_completion`) for monitoring
- Configuration rarely changes

**Use `with_options()` When:**
- Configuration depends on runtime data (dataset size, API response characteristics)
- You need different behavior for different scenarios (development vs. production)
- You want to create multiple variants of the same task with different reliability profiles
- Configuration is determined by external factors (time of day, system load, data source)
- You're building reusable workflows that need to adapt to different environments

**Combine Both When:**
- You have sensible defaults in decorators but need runtime overrides
- You want base monitoring (hooks) with adaptive retry behavior
- You need fallback strategies with different configurations
- You're building enterprise workflows that need both consistency and flexibility

Key concepts you just learned:
- **Direct decorator parameters** - `@flow(retries=2, timeout_seconds=120, on_failure=hook)`
- **Dynamic configuration** - `task.with_options(retries=5, retry_delay_seconds=30)`
- **Flow hooks** - `on_failure` and `on_completion` for monitoring and cleanup
- **When to use each approach** - Static vs dynamic configuration needs
- **Combining approaches** - Base configuration + runtime overrides

Try running these examples to see both approaches in action:

```run
python3 direct_decorator_example.py
```

```run
python3 dynamic_configuration_example.py
```

Now let's use a real API with more advanced flow-level configuration:

```python
import requests
import time
import os
from datetime import timedelta
from prefect import flow, task, get_run_logger

@task
def fetch_github_repos(owner: str):
    """Fetch GitHub repositories with proper authentication"""
    logger = get_run_logger()
    logger.info(f"Fetching repositories for {owner}")

    # Use GitHub token if available to avoid rate limits
    headers = {}
    github_token = os.getenv('GITHUB_TOKEN')
    if github_token:
        headers['Authorization'] = f'token {github_token}'
        logger.info("Using authenticated GitHub API request")
    else:
        logger.warning("No GITHUB_TOKEN found - using unauthenticated requests (rate limited)")

    response = requests.get(f"https://api.github.com/users/{owner}/repos", headers=headers)
    response.raise_for_status()
    return response.json()

@task
def analyze_repository(repo_data, analysis_depth: str = "standard"):
    """Analyze repository with configurable depth"""
    logger = get_run_logger()

    # Simulate different analysis depths
    if analysis_depth == "deep":
        time.sleep(2)  # Deep analysis
    elif analysis_depth == "shallow":
        time.sleep(0.3)  # Quick analysis
    else:
        time.sleep(0.8)  # Standard analysis

    # Simulate analysis failures for certain conditions
    if repo_data["stargazers_count"] > 10000 and analysis_depth == "shallow":
        raise Exception(f"Shallow analysis insufficient for popular repo: {repo_data['name']}")

    return {
        "name": repo_data["name"],
        "stars": repo_data["stargazers_count"],
        "forks": repo_data["forks_count"],
        "language": repo_data["language"],
        "analysis_depth": analysis_depth,
        "popularity_score": repo_data["stargazers_count"] + (repo_data["forks_count"] * 2)
    }

@flow
def analyze_single_repo(repo_data, analysis_depth: str = "standard"):
    """Analyze a single repository - subflow"""
    logger = get_run_logger()
    logger.info(f"Analyzing repository: {repo_data['name']}")

    analysis = analyze_repository(repo_data, analysis_depth)
    return analysis

@flow(name="github-analysis-{strategy}-{owner}")
def advanced_github_analysis(owner: str = "PrefectHQ", processing_strategy: str = "balanced"):
    """Advanced GitHub analysis with dynamic flow configuration"""
    logger = get_run_logger()
    logger.info(f"Starting GitHub analysis for {owner} with {processing_strategy} strategy")

    # Fetch repositories to understand scope
    repos = fetch_github_repos(owner)
    repo_count = len(repos)
    total_stars = sum(repo.get("stargazers_count", 0) for repo in repos)

    logger.info(f"Found {repo_count} repositories with {total_stars} total stars")

    # Configure strategy based on repository characteristics and strategy
    if processing_strategy == "thorough" or total_stars > 50000:
        # Thorough processing for popular owners
        flow_config = {
            "retries": 4,
            "retry_delay_seconds": 45,
            "timeout_seconds": 600
        }
        task_config = {
            "retries": 3,
            "retry_delay_seconds": 20,
            "cache_expiration": timedelta(hours=2)
        }
        analysis_depth = "deep"
        logger.info("Using thorough processing for high-profile repositories")

    elif processing_strategy == "quick":
        # Quick processing
        flow_config = {
            "retries": 1,
            "retry_delay_seconds": 10,
            "timeout_seconds": 120
        }
        task_config = {
            "retries": 1,
            "retry_delay_seconds": 5
        }
        analysis_depth = "shallow"
        logger.info("Using quick processing for fast results")

    else:
        # Balanced processing
        flow_config = {
            "retries": 2,
            "retry_delay_seconds": 25,
            "timeout_seconds": 300
        }
        task_config = {
            "retries": 2,
            "retry_delay_seconds": 12,
            "cache_expiration": timedelta(minutes=30)
        }
        analysis_depth = "standard"
        logger.info("Using balanced processing configuration")

    # Create dynamically configured task (flows don't use with_options() the same way)
    configured_analyze_task = analyze_repository.with_options(**task_config)

    # Process repositories with adaptive configuration
    analyses = []
    successful_analyses = 0

    # Limit to first 5 repos for demo
    for repo in repos[:5]:
        try:
            # Use subflow with our configured task
            analysis = analyze_single_repo(repo, analysis_depth)
            analyses.append(analysis)
            successful_analyses += 1
            logger.info(f"Successfully analyzed {repo['name']}")
        except Exception as e:
            logger.error(f"Failed to analyze {repo['name']}: {str(e)}")
            # Add error record but continue
            analyses.append({
                "name": repo["name"],
                "error": str(e),
                "status": "failed"
            })

    # Calculate summary
    return {
        "owner": owner,
        "processing_strategy": processing_strategy,
        "total_repos": repo_count,
        "analyzed_repos": len(analyses),
        "successful_analyses": successful_analyses,
        "analysis_depth": analysis_depth,
        "flow_config": flow_config,
        "task_config": task_config,
        "analyses": analyses
    }

if __name__ == "__main__":
    # Test different processing strategies with real GitHub data
    strategies = ["quick", "balanced", "thorough"]
    owners = ["PrefectHQ", "pandas-dev"]  # Different complexity levels

    for owner in owners:
        for strategy in strategies:
            print(f"\n=== Analyzing {owner} with {strategy} strategy ===")
            result = advanced_github_analysis(owner, strategy)
            print(f"Owner: {result['owner']}")
            print(f"Strategy: {result['processing_strategy']}")
            print(f"Success rate: {result['successful_analyses']}/{result['analyzed_repos']}")
            print(f"Flow config: {result['flow_config']}")
```

**Key concepts you just learned:**
- **Task-level `with_options()`** - Dynamic task configuration including timeouts and retries
- **Strategy-based configuration** - Predefined configuration patterns for different scenarios
- **Cache configuration** - Dynamic cache expiration (`timedelta(hours=2)`) based on processing needs
- **Authentication handling** - Proper API token usage for production workflows
- **Graceful degradation** - Continue processing even when individual items fail

Run this to see advanced configuration with real GitHub data:

**Note:** For best results, set a GitHub token to avoid rate limits:
```bash
export GITHUB_TOKEN="your_token_here"
python3 advanced_github_analysis.py
```

Or run without authentication (limited requests):
```run
python3 advanced_github_analysis.py
```

What You've Accomplished
===

🎉 **Congratulations!** You've transformed from writing rigid, one-size-fits-all workflows to building intelligent, adaptive systems. You now understand:

**The Business Impact:**
- **Cost Savings** - No more over-provisioning resources for simple tasks
- **Reliability** - Critical processes get the retry and timeout protection they need
- **Performance** - Workflows adapt to actual conditions instead of worst-case assumptions
- **Maintainability** - One codebase handles multiple scenarios intelligently

**Technical Mastery:**

✅ **Direct decorator parameters** - Static configuration with hooks for monitoring and cleanup
✅ **Dynamic `with_options()` configuration** - Runtime configuration based on data characteristics
✅ **Flow hooks** - `on_failure` and `on_completion` for robust monitoring and error handling
✅ **Adaptive decision-making** - Configuration choices based on actual data characteristics
✅ **Strategy patterns** - Predefined configuration sets for different processing requirements
✅ **Fallback handling** - Graceful degradation with alternative configurations when primary approaches fail
✅ **Combined approaches** - Base configuration + runtime overrides for maximum flexibility
✅ **Real API integration** - Applied both approaches to actual APIs like JSONPlaceholder and GitHub

These concepts form the foundation of truly flexible workflows that adapt to real-world variability and optimize performance based on actual conditions, using the right configuration approach for each situation.

Next Steps
===

You're now ready for **Challenge 2: Transactions & Data Consistency**, where you'll learn:
- Prefect transactions for atomic operations
- Rollback patterns and error recovery
- Data consistency across multi-step operations
- Database transactions with workflow state

The journey into advanced Prefect SDK capabilities continues! 🚀

Additional Resources
===

- [Prefect Task Options Documentation](https://docs.prefect.io/v3/api-ref/python/prefect-tasks#with-options)
- [Prefect Flow Options](https://docs.prefect.io/v3/api-ref/python/prefect-flows#with-options)
- [Dynamic Task Configuration Patterns](https://docs.prefect.io/concepts/tasks/#task-configuration)
- [JSONPlaceholder API](https://jsonplaceholder.typicode.com/)
- [GitHub API Documentation](https://docs.github.com/en/rest)