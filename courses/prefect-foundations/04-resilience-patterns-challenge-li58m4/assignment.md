---
slug: resilience-patterns-challenge-li58m4
id: uf8hdesrlqxv
type: challenge
title: Resilience & Patterns
teaser: In this track, you'll learn advanced patterns that make your workflows resilient,
  maintainable, and production-safe. We'll focus on conditional logic, modular design,
  and handling complex real-world scenarios.
notes:
- type: text
  contents: |2-

    # Why Resilience & Patterns Matter
    **The Problem**: Real-world workflows face unpredictable conditions.

    - Varying data volumes and environments
    - Network issues and changing requirements
    - Simple linear flows break when reality gets messy

    **The Cost**:
    - Unreliable business operations
    - Data quality issues
    - Maintenance nightmares
    - Lost trust from stakeholders

    **The Solution**: Prefect provides patterns for building resilient, adaptive workflows that handle real-world complexity.
- type: text
  contents: |-
    # Conditional Logic & Runtime Context
    **Key Concept**: Build intelligent workflows that adapt to their environment.

    **Conditional Logic**:
    - Workflows that adapt to different data and conditions
    - Graceful error handling with fallback strategies
    - Resilient workflows that handle edge cases

    **Runtime Context**:
    - Access flow run, task run, and deployment information
    - Context-aware decision making
    - Intelligent metadata for traceability
    - Deployment-aware processing strategies

    **Real Example**: User data processing that handles missing users gracefully and adapts behavior based on deployment context.
- type: text
  contents: |-
    # Modular Design with Subflows
    **Key Concept**: Create reusable, maintainable workflow components.

    **What you learned**:
    - `@flow` decorator creates reusable subflows
    - Subflows can be called from other flows
    - Modular design makes workflows easier to test and maintain
    - Reusable components reduce code duplication

    **Real Example**: ETL pipeline refactored from monolithic to modular design with reusable subflows for different data types.

    **Result**: Clean, organized workflows that are easy to test, debug, and maintain.
tabs:
- id: lfrmxfhv3p7i
  title: "\U0001F4BB Terminal"
  type: terminal
  hostname: prefect-sandbox
  cmd: /bin/bash
- id: m74lxdahx1pj
  title: "\U0001F6A7 Code Editor"
  type: code
  hostname: prefect-sandbox
  path: /root
difficulty: ""
enhanced_loading: null
---
Introduction
===

Production workflows need to handle real-world complexity. This track covers advanced patterns that make your workflows resilient and maintainable.

You'll learn:
- **Conditional logic** - Adapt to different data and environments
- **Subflows** - Create modular, reusable components
- **Runtime context** - Make workflows aware of their execution environment
- **Idempotency** - Ensure data consistency across runs
- **Error handling** - Manage edge cases without breaking workflows

Let's build workflows that work in production.

Setup Your Project
===

Let's set up your environment for building resilient workflows with Prefect.

We'll use `uv` for package management.

**Install UV package manager:**

```run
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
uv --version
```

**Set up your project environment:**

First, let's check if you already have a virtual environment from previous challenges:

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

**Install dependencies for this challenge:**

```run
uv pip install requests
```

Why Resilience Matters
===

Real-world workflows face unpredictable conditions. Data volumes change, networks fail, APIs return unexpected responses. Simple linear flows break when things get messy.

Without resilience patterns:
- Workflows fail on unexpected data
- Code becomes hard to maintain
- Duplicate processing creates inconsistencies
- Edge cases cause silent failures

This costs you reliable operations, data quality, and stakeholder trust.

Why Patterns Matter
===

Without established patterns, every workflow becomes unique. This creates inconsistent behavior, hard-to-maintain code, and repeated mistakes.

You need:
- Reusable components that work across scenarios
- Consistent error handling
- Modular design that's easy to test
- Proven approaches to common challenges

Prefect gives you these patterns. Here's how to use them.

Conditional Logic & Dynamic Flows
===

Workflows need to adapt to different conditions. Let's build one that handles real API responses, including edge cases.

Start with a basic workflow that doesn't handle errors or unexpected data.

**Create your basic user flow file:**

```run
touch simple_user_flow.py
```

Add this code to `simple_user_flow.py`:

```python
from prefect import flow, task
import requests

@task
def fetch_user_data(user_id: int):
    """Fetch user data from API"""
    response = requests.get(f"https://jsonplaceholder.typicode.com/users/{user_id}")
    response.raise_for_status()
    return response.json()

@task
def process_user_data(user_data):
    """Process user data"""
    return {
        "id": user_data["id"],
        "name": user_data["name"],
        "email": user_data["email"],
        "status": "processed"
    }

@flow
def simple_user_flow(user_id: int):
    """Simple user processing flow"""
    user_data = fetch_user_data(user_id)
    processed = process_user_data(user_data)
    return processed

if __name__ == "__main__":
    result = simple_user_flow(1)
    print(f"Processed user: {result}")
```

**Test the basic version:**

```run
uv run simple_user_flow.py
```

This works for valid users, but what about edge cases? Let's make it resilient with conditional logic.

**Create the resilient version:**

```run
touch resilient_user_flow.py
```

Add this code to `resilient_user_flow.py`:

```python
from prefect import flow, task, get_run_logger
import requests

@task
def fetch_user_data(user_id: int):
    """Fetch user data with error handling"""
    logger = get_run_logger()

    try:
        response = requests.get(f"https://jsonplaceholder.typicode.com/users/{user_id}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch user {user_id}: {str(e)}")
        return None

@task
def process_user_data(user_data):
    """Process user data with validation"""
    logger = get_run_logger()

    if not user_data:
        logger.warning("No user data to process")
        return None

    return {
        "id": user_data["id"],
        "name": user_data["name"],
        "email": user_data["email"],
        "status": "processed"
    }

@task
def handle_missing_user(user_id: int):
    """Handle case when user doesn't exist"""
    logger = get_run_logger()
    logger.warning(f"User {user_id} not found, creating placeholder")
    return {
        "id": user_id,
        "name": "Unknown User",
        "email": "unknown@example.com",
        "status": "placeholder"
    }

@flow(name="resilient-user-flow-{user_id}")
def resilient_user_flow(user_id: int):
    """Resilient user processing with conditional logic"""
    logger = get_run_logger()
    logger.info(f"Processing user {user_id}")

    # Fetch user data
    user_data = fetch_user_data(user_id)

    # Conditional processing based on data availability
    if user_data:
        processed = process_user_data(user_data)
        logger.info(f"Successfully processed user {user_id}")
    else:
        processed = handle_missing_user(user_id)
        logger.warning(f"Used placeholder for user {user_id}")

    return processed

if __name__ == "__main__":
    # Test with valid user
    result1 = resilient_user_flow(1)
    print(f"Valid user: {result1}")

    # Test with invalid user (should trigger conditional logic)
    result2 = resilient_user_flow(999)
    print(f"Invalid user: {result2}")
```

This version handles errors and missing data:
- Check if data exists before processing
- Handle API failures without crashing
- Log what's happening for debugging
- Provide fallback behavior for edge cases

Run it:

```run
uv run resilient_user_flow.py
```

Now let's handle multiple conditions. We'll build a workflow that adapts based on what it finds in a GitHub repository.

**Create the adaptive repository analysis file:**

```run
touch adaptive_repo_analysis.py
```

Add this code to `adaptive_repo_analysis.py`:

```python
from prefect import flow, task, get_run_logger
import requests

@task
def fetch_repository_info(owner: str, repo: str):
    """Fetch repository information"""
    logger = get_run_logger()

    try:
        response = requests.get(f"https://api.github.com/repos/{owner}/{repo}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch {owner}/{repo}: {str(e)}")
        return None

@task
def analyze_repository(repo_data):
    """Analyze repository based on its characteristics"""
    logger = get_run_logger()

    if not repo_data:
        return {"status": "not_found", "action": "skip"}

    stars = repo_data.get("stargazers_count", 0)
    forks = repo_data.get("forks_count", 0)
    language = repo_data.get("language", "Unknown")

    # Conditional analysis based on repository characteristics
    if stars > 1000:
        return {
            "status": "popular",
            "action": "detailed_analysis",
            "priority": "high",
            "stars": stars,
            "forks": forks,
            "language": language
        }
    elif stars > 100:
        return {
            "status": "moderate",
            "action": "standard_analysis",
            "priority": "medium",
            "stars": stars,
            "forks": forks,
            "language": language
        }
    else:
        return {
            "status": "new",
            "action": "basic_analysis",
            "priority": "low",
            "stars": stars,
            "forks": forks,
            "language": language
        }

@task
def detailed_analysis(repo_data):
    """Perform detailed analysis for popular repositories"""
    logger = get_run_logger()
    logger.info("Performing detailed analysis for popular repository")

    return {
        "analysis_type": "detailed",
        "recommendations": [
            "Monitor for security updates",
            "Consider enterprise features",
            "Track community engagement"
        ]
    }

@task
def standard_analysis(repo_data):
    """Perform standard analysis for moderate repositories"""
    logger = get_run_logger()
    logger.info("Performing standard analysis for moderate repository")

    return {
        "analysis_type": "standard",
        "recommendations": [
            "Monitor growth trends",
            "Check documentation quality"
        ]
    }

@task
def basic_analysis(repo_data):
    """Perform basic analysis for new repositories"""
    logger = get_run_logger()
    logger.info("Performing basic analysis for new repository")

    return {
        "analysis_type": "basic",
        "recommendations": [
            "Focus on initial development",
            "Build community presence"
        ]
    }

@flow(name="adaptive-repo-analysis-{owner}-{repo}")
def adaptive_repo_analysis(owner: str, repo: str):
    """Adaptive repository analysis with conditional logic"""
    logger = get_run_logger()
    logger.info(f"Starting adaptive analysis for {owner}/{repo}")

    # Fetch repository data
    repo_data = fetch_repository_info(owner, repo)

    # Analyze repository characteristics
    analysis_plan = analyze_repository(repo_data)

    # Execute different analysis based on repository status
    if analysis_plan["action"] == "detailed_analysis":
        result = detailed_analysis(repo_data)
    elif analysis_plan["action"] == "standard_analysis":
        result = standard_analysis(repo_data)
    elif analysis_plan["action"] == "basic_analysis":
        result = basic_analysis(repo_data)
    else:
        logger.warning(f"Skipping analysis for {owner}/{repo}")
        result = {"analysis_type": "skipped", "reason": "repository_not_found"}

    return {
        "repository": f"{owner}/{repo}",
        "analysis_plan": analysis_plan,
        "result": result
    }

if __name__ == "__main__":
    # Test with different types of repositories
    repos = [
        ("PrefectHQ", "prefect"),  # Popular
        ("pandas-dev", "pandas"),  # Popular
        ("your-username", "test-repo"),  # Likely not found
    ]

    for owner, repo in repos:
        result = adaptive_repo_analysis(owner, repo)
        print(f"\n{owner}/{repo}: {result['analysis_plan']['status']} - {result['result']['analysis_type']}")
```

Run it:

```run
uv run adaptive_repo_analysis.py
```

Runtime Context & Context-Aware Workflows
===

Workflows often need to know where and how they're running. Prefect gives you access to runtime information so your code can adapt.

**How to Access Runtime Context**

Two ways to access the same data:

```python
# Approach 1: Namespace (used in this course)
from prefect import runtime
flow_name = runtime.flow_run.name
task_name = runtime.task_run.name

# Approach 2: Direct import (also valid)
from prefect.runtime import flow_run, task_run
flow_name = flow_run.name
task_name = task_run.name

# Both access the exact same data!
```

**Key Points:**
- Both approaches are functionally identical
- Attributes return `None` if not available (never raise errors)
- The namespace approach (`prefect.runtime`) is more explicit about what you're accessing
- Direct imports are more concise but less clear about the source

First, let's create a workflow that doesn't use runtime context.

**Create your basic data flow file:**

```run
touch basic_data_flow.py
```

Add this code to `basic_data_flow.py`:

```python
from prefect import flow, task
import requests

@task
def fetch_data(source: str):
    """Fetch data from API"""
    response = requests.get(f"https://jsonplaceholder.typicode.com/{source}")
    response.raise_for_status()
    return response.json()

@task
def process_data(data, data_type: str):
    """Process data"""
    return [{"id": item["id"], "title": item.get("title", item.get("name", "Unknown"))} for item in data]

@flow
def basic_data_flow(data_type: str):
    """Basic data processing flow"""
    data = fetch_data(data_type)
    processed = process_data(data, data_type)
    return processed

if __name__ == "__main__":
    result = basic_data_flow("users")
    print(f"Processed {len(result)} items")
```

**Test the basic version:**

```run
uv run basic_data_flow.py
```

This works but doesn't take advantage of runtime information. Let's make it context-aware.

**Create the context-aware version:**

```run
touch context_aware_data_flow.py
```

Add this code to `context_aware_data_flow.py`:

```python
from prefect import flow, task, get_run_logger
from prefect import runtime
import requests
import json
from datetime import datetime

@task
def fetch_data_with_context(source: str):
    """Fetch data with runtime context awareness"""
    logger = get_run_logger()

    # Access runtime information
    flow_name = runtime.flow_run.name
    task_name = runtime.task_run.name
    flow_parameters = runtime.flow_run.parameters

    logger.info(f"Fetching {source} data in flow '{flow_name}' with task '{task_name}'")
    logger.info(f"Flow parameters: {flow_parameters}")

    response = requests.get(f"https://jsonplaceholder.typicode.com/{source}")
    response.raise_for_status()
    return response.json()

@task
def process_data_with_context(data, data_type: str):
    """Process data with runtime context awareness"""
    logger = get_run_logger()

    # Access runtime information
    task_name = runtime.task_run.name
    flow_name = runtime.flow_run.name

    logger.info(f"Processing {len(data)} {data_type} items in task '{task_name}'")

    processed = []
    for i, item in enumerate(data):
        processed.append({
            "id": item["id"],
            "title": item.get("title", item.get("name", "Unknown")),
            "processed_by": task_name,
            "flow_name": flow_name,
            "processing_order": i + 1
        })

    return processed

@task
def save_results_with_context(processed_data, data_type: str):
    """Save results with runtime context metadata"""
    logger = get_run_logger()

    # Access runtime information
    flow_name = runtime.flow_run.name
    flow_id = runtime.flow_run.id
    deployment_name = runtime.deployment.name if runtime.deployment else "local"

    # Add runtime metadata to results
    results_with_metadata = {
        "data_type": data_type,
        "processed_count": len(processed_data),
        "flow_name": flow_name,
        "flow_id": str(flow_id),
        "deployment_name": deployment_name,
        "processing_timestamp": datetime.now().isoformat(),
        "data": processed_data
    }

    filename = f"{data_type}_{flow_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(filename, 'w') as f:
        json.dump(results_with_metadata, f, indent=2)

    logger.info(f"Saved {len(processed_data)} {data_type} items to {filename}")
    return filename

@flow(name="context-aware-data-flow-{data_type}")
def context_aware_data_flow(data_type: str):
    """Context-aware data processing flow"""
    logger = get_run_logger()

    # Access flow-level runtime information
    flow_name = runtime.flow_run.name
    flow_id = runtime.flow_run.id
    deployment_name = runtime.deployment.name if runtime.deployment else "local"

    logger.info(f"Starting context-aware flow '{flow_name}' (ID: {flow_id})")
    logger.info(f"Deployment: {deployment_name}")
    logger.info(f"Processing data type: {data_type}")

    # Fetch data
    data = fetch_data_with_context(data_type)

    # Process data
    processed = process_data_with_context(data, data_type)

    # Save results
    filename = save_results_with_context(processed, data_type)

    return {
        "data_type": data_type,
        "processed_count": len(processed),
        "output_file": filename,
        "flow_name": flow_name,
        "flow_id": str(flow_id)
    }

if __name__ == "__main__":
    result = context_aware_data_flow("posts")
    print(f"Context-aware processing complete: {result}")
```

What you can access:
- `runtime.flow_run.name` - Current flow run name
- `runtime.task_run.name` - Current task run name
- `runtime.flow_run.parameters` - Flow parameters
- `runtime.deployment.name` - Deployment info

Run it:

```run
uv run context_aware_data_flow.py
```

Now let's use runtime context to make decisions. This example changes behavior based on deployment status.

**Create the intelligent context flow file:**

```run
touch intelligent_context_flow.py
```

Add this code to `intelligent_context_flow.py`:

```python
from prefect import flow, task, get_run_logger
from prefect import runtime
import requests
import json
from datetime import datetime

@task
def intelligent_data_fetch(source: str, limit: int = None):
    """Intelligently fetch data based on runtime context"""
    logger = get_run_logger()

    # Access runtime information for intelligent decisions
    flow_name = runtime.flow_run.name
    flow_parameters = runtime.flow_run.parameters
    deployment_name = runtime.deployment.name if runtime.deployment else "local"

    # Determine fetch strategy based on context
    if deployment_name == "production":
        # Production: fetch more data, be more thorough
        actual_limit = limit or 100
        logger.info(f"Production mode: fetching up to {actual_limit} {source} items")
    elif "test" in flow_name.lower():
        # Test mode: fetch minimal data for speed
        actual_limit = min(limit or 10, 10)
        logger.info(f"Test mode: fetching {actual_limit} {source} items for speed")
    else:
        # Development mode: moderate amount
        actual_limit = limit or 50
        logger.info(f"Development mode: fetching {actual_limit} {source} items")

    # Fetch data with limit
    url = f"https://jsonplaceholder.typicode.com/{source}"
    if actual_limit:
        url += f"?_limit={actual_limit}"

    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    # Add context metadata to each item
    for item in data:
        item["_runtime_metadata"] = {
            "fetched_by": runtime.task_run.name,
            "flow_name": flow_name,
            "deployment": deployment_name,
            "fetch_timestamp": datetime.now().isoformat()
        }

    return data

@task
def adaptive_processing(data, data_type: str):
    """Adapt processing based on runtime context"""
    logger = get_run_logger()

    # Access runtime information
    flow_name = runtime.flow_run.name
    deployment_name = runtime.deployment.name if runtime.deployment else "local"

    # Determine processing strategy based on context
    if deployment_name == "production":
        # Production: full processing with validation
        logger.info("Production processing: full validation and enrichment")
        processed = []
        for item in data:
            processed.append({
                "id": item["id"],
                "title": item.get("title", item.get("name", "Unknown")),
                "body": item.get("body", item.get("email", "")),
                "processed_by": runtime.task_run.name,
                "processing_mode": "production",
                "validation_status": "validated",
                "runtime_metadata": item.get("_runtime_metadata", {})
            })
    else:
        # Non-production: simplified processing
        logger.info("Non-production processing: simplified for speed")
        processed = []
        for item in data:
            processed.append({
                "id": item["id"],
                "title": item.get("title", item.get("name", "Unknown")),
                "processed_by": runtime.task_run.name,
                "processing_mode": "development",
                "runtime_metadata": item.get("_runtime_metadata", {})
            })

    return processed

@task
def context_aware_save(processed_data, data_type: str):
    """Save data with context-aware naming and metadata"""
    logger = get_run_logger()

    # Access runtime information
    flow_name = runtime.flow_run.name
    flow_id = runtime.flow_run.id
    deployment_name = runtime.deployment.name if runtime.deployment else "local"

    # Create context-aware filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{data_type}_{deployment_name}_{flow_name}_{timestamp}.json"

    # Create comprehensive metadata
    metadata = {
        "processing_summary": {
            "data_type": data_type,
            "processed_count": len(processed_data),
            "flow_name": flow_name,
            "flow_id": str(flow_id),
            "deployment_name": deployment_name,
            "processing_timestamp": datetime.now().isoformat()
        },
        "runtime_context": {
            "flow_parameters": runtime.flow_run.parameters,
            "flow_run_name": runtime.flow_run.name,
            "deployment_id": str(runtime.deployment.id) if runtime.deployment else None
        },
        "data": processed_data
    }

    with open(filename, 'w') as f:
        json.dump(metadata, f, indent=2)

    logger.info(f"Saved {len(processed_data)} {data_type} items to {filename}")
    logger.info(f"Deployment: {deployment_name}, Flow: {flow_name}")

    return filename

@flow(name="intelligent-context-flow-{data_type}")
def intelligent_context_flow(data_type: str, limit: int = None):
    """Intelligent workflow that adapts based on runtime context"""
    logger = get_run_logger()

    # Access and log runtime context
    flow_name = runtime.flow_run.name
    flow_id = runtime.flow_run.id
    deployment_name = runtime.deployment.name if runtime.deployment else "local"

    logger.info(f"Starting intelligent flow '{flow_name}' (ID: {flow_id})")
    logger.info(f"Deployment context: {deployment_name}")
    logger.info(f"Flow parameters: {runtime.flow_run.parameters}")

    # Intelligently fetch data based on context
    data = intelligent_data_fetch(data_type, limit)

    # Adapt processing based on context
    processed = adaptive_processing(data, data_type)

    # Save with context-aware metadata
    filename = context_aware_save(processed, data_type)

    return {
        "data_type": data_type,
        "processed_count": len(processed),
        "output_file": filename,
        "flow_name": flow_name,
        "deployment": deployment_name,
        "processing_mode": "production" if deployment_name == "production" else "development"
    }

if __name__ == "__main__":
    # Test with different contexts
    result = intelligent_context_flow("posts", limit=20)
    print(f"Intelligent processing complete: {result}")
```

Run it:

```run
uv run intelligent_context_flow.py
```

Notice how it adapts based on where it's running. Production deployments get different behavior than local runs.

Subflows & Modular Design
===

Large workflows get messy fast. Subflows let you break them into reusable pieces.

Start with a monolithic workflow that does everything in one place.

**Create the monolithic ETL file:**

```run
touch monolithic_etl.py
```

Add this code to `monolithic_etl.py`:

```python
from prefect import flow, task
import requests
import json

@task
def fetch_data(source: str):
    """Fetch data from different sources"""
    if source == "users":
        response = requests.get("https://jsonplaceholder.typicode.com/users")
    elif source == "posts":
        response = requests.get("https://jsonplaceholder.typicode.com/posts")
    else:
        raise ValueError(f"Unknown source: {source}")

    response.raise_for_status()
    return response.json()

@task
def process_data(data, data_type: str):
    """Process different types of data"""
    if data_type == "users":
        return [{"id": item["id"], "name": item["name"], "email": item["email"]} for item in data]
    elif data_type == "posts":
        return [{"id": item["id"], "title": item["title"], "body": item["body"][:100]} for item in data]
    else:
        raise ValueError(f"Unknown data type: {data_type}")

@task
def save_data(data, filename: str):
    """Save data to file"""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    return f"Saved {len(data)} records to {filename}"

@flow
def monolithic_etl():
    """Monolithic ETL workflow"""
    # Process users
    user_data = fetch_data("users")
    processed_users = process_data(user_data, "users")
    save_data(processed_users, "users.json")

    # Process posts
    post_data = fetch_data("posts")
    processed_posts = process_data(post_data, "posts")
    save_data(processed_posts, "posts.json")

    return "ETL completed"

if __name__ == "__main__":
    result = monolithic_etl()
    print(result)
```

**Test the monolithic version:**

```run
uv run monolithic_etl.py
```

This works but isn't modular. Let's refactor it using subflows.

**Create the modular ETL pipeline file:**

```run
touch modular_etl_pipeline.py
```

Add this code to `modular_etl_pipeline.py`:

```python
from prefect import flow, task
import requests
import json

@task
def fetch_data(source: str):
    """Fetch data from different sources"""
    if source == "users":
        response = requests.get("https://jsonplaceholder.typicode.com/users")
    elif source == "posts":
        response = requests.get("https://jsonplaceholder.typicode.com/posts")
    else:
        raise ValueError(f"Unknown source: {source}")

    response.raise_for_status()
    return response.json()

@task
def process_data(data, data_type: str):
    """Process different types of data"""
    if data_type == "users":
        return [{"id": item["id"], "name": item["name"], "email": item["email"]} for item in data]
    elif data_type == "posts":
        return [{"id": item["id"], "title": item["title"], "body": item["body"][:100]} for item in data]
    else:
        raise ValueError(f"Unknown data type: {data_type}")

@task
def save_data(data, filename: str):
    """Save data to file"""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    return f"Saved {len(data)} records to {filename}"

@flow(name="etl-{data_type}")
def etl_subflow(data_type: str, source: str, filename: str):
    """Reusable ETL subflow for any data type"""
    # Extract
    raw_data = fetch_data(source)

    # Transform
    processed_data = process_data(raw_data, data_type)

    # Load
    result = save_data(processed_data, filename)

    return {
        "data_type": data_type,
        "records_processed": len(processed_data),
        "filename": filename,
        "status": "completed"
    }

@flow(name="modular-etl-pipeline")
def modular_etl_pipeline():
    """Modular ETL pipeline using subflows"""
    # Process users using subflow
    user_result = etl_subflow("users", "users", "users.json")

    # Process posts using subflow
    post_result = etl_subflow("posts", "posts", "posts.json")

    return {
        "user_etl": user_result,
        "post_etl": post_result,
        "overall_status": "completed"
    }

if __name__ == "__main__":
    result = modular_etl_pipeline()
    print(f"ETL Pipeline Results: {result}")
```

This version uses subflows:
- Each `@flow` can be called independently
- Test and debug components separately
- Reuse them across different workflows
- Maintain each piece on its own

Run it:

```run
uv run modular_etl_pipeline.py
```

Now let's nest subflows inside other subflows to handle complex workflows.

**Create the GitHub ecosystem analysis file:**

```run
touch github_ecosystem_analysis.py
```

Add this code to `github_ecosystem_analysis.py`:

```python
from prefect import flow, task, get_run_logger
import requests
import json
from datetime import datetime

@task
def fetch_github_repos(owner: str):
    """Fetch repositories for a GitHub user/organization"""
    logger = get_run_logger()
    logger.info(f"Fetching repositories for {owner}")

    response = requests.get(f"https://api.github.com/users/{owner}/repos")
    response.raise_for_status()
    return response.json()

@task
def analyze_repository(repo_data):
    """Analyze a single repository"""
    return {
        "name": repo_data["name"],
        "stars": repo_data["stargazers_count"],
        "forks": repo_data["forks_count"],
        "language": repo_data["language"],
        "size": repo_data["size"],
        "created_at": repo_data["created_at"],
        "updated_at": repo_data["updated_at"]
    }

@flow(name="analyze-repo-{repo_name}")
def analyze_repository_subflow(repo_data):
    """Subflow to analyze a single repository"""
    logger = get_run_logger()
    logger.info(f"Analyzing repository: {repo_data['name']}")

    analysis = analyze_repository(repo_data)

    # Add some derived metrics
    analysis["popularity_score"] = analysis["stars"] + (analysis["forks"] * 2)
    analysis["age_days"] = (datetime.now() - datetime.fromisoformat(analysis["created_at"].replace('Z', '+00:00'))).days

    return analysis

@flow(name="analyze-owner-{owner}")
def analyze_owner_subflow(owner: str):
    """Subflow to analyze all repositories for an owner"""
    logger = get_run_logger()
    logger.info(f"Starting analysis for owner: {owner}")

    # Fetch all repositories
    repos = fetch_github_repos(owner)

    # Analyze each repository using subflows
    analyses = []
    for repo in repos:
        analysis = analyze_repository_subflow(repo)
        analyses.append(analysis)

    # Calculate summary statistics
    total_stars = sum(analysis["stars"] for analysis in analyses)
    total_forks = sum(analysis["forks"] for analysis in analyses)
    languages = list(set(analysis["language"] for analysis in analyses if analysis["language"]))

    return {
        "owner": owner,
        "total_repos": len(analyses),
        "total_stars": total_stars,
        "total_forks": total_forks,
        "languages": languages,
        "repositories": analyses
    }

@task
def save_analysis(analysis_data, filename: str):
    """Save analysis results to file"""
    with open(filename, 'w') as f:
        json.dump(analysis_data, f, indent=2)
    return f"Analysis saved to {filename}"

@flow(name="github-ecosystem-analysis")
def github_ecosystem_analysis(owners: list):
    """Main flow that analyzes multiple GitHub owners using subflows"""
    logger = get_run_logger()
    logger.info(f"Starting ecosystem analysis for {len(owners)} owners")

    # Analyze each owner using subflows
    owner_analyses = []
    for owner in owners:
        analysis = analyze_owner_subflow(owner)
        owner_analyses.append(analysis)

    # Save individual analyses
    for analysis in owner_analyses:
        filename = f"{analysis['owner']}_analysis.json"
        save_analysis(analysis, filename)

    # Calculate ecosystem summary
    total_repos = sum(analysis["total_repos"] for analysis in owner_analyses)
    total_stars = sum(analysis["total_stars"] for analysis in owner_analyses)
    all_languages = set()
    for analysis in owner_analyses:
        all_languages.update(analysis["languages"])

    ecosystem_summary = {
        "owners_analyzed": len(owners),
        "total_repositories": total_repos,
        "total_stars": total_stars,
        "languages_used": list(all_languages),
        "analysis_timestamp": datetime.now().isoformat()
    }

    # Save ecosystem summary
    save_analysis(ecosystem_summary, "ecosystem_summary.json")

    return ecosystem_summary

if __name__ == "__main__":
    owners = ["PrefectHQ", "pandas-dev", "numpy"]
    result = github_ecosystem_analysis(owners)
    print(f"Ecosystem Analysis Complete: {result}")
```

Run it:

```run
uv run github_ecosystem_analysis.py
```

What You've Built
===

You now have patterns for production workflows:

- **Conditional logic** - Handle different data and edge cases
- **Runtime context** - Adapt based on execution environment
- **Modular design** - Break workflows into reusable pieces
- **Error handling** - Fail gracefully, not catastrophically
- **Real APIs** - Work with actual data sources

These patterns handle real-world complexity.

Next Steps
===

Ready for **Orchestration & Scale**:
- Parallel execution for high-throughput
- Work pools and queues
- Resource limits
- Enterprise scaling patterns

Additional Resources
===

- [Prefect Runtime Context Documentation](https://docs.prefect.io/v3/concepts/runtime-context)
- [Prefect How-to: Access Runtime Information](https://docs.prefect.io/v3/how-to-guides/workflows/access-runtime-info)
- [Prefect Subflows Documentation](https://docs.prefect.io/concepts/flows/#composing-flows)
- [Prefect Conditional Logic](https://docs.prefect.io/concepts/flows/#conditional-logic)
- [Prefect Error Handling](https://docs.prefect.io/concepts/flows/#error-handling)
- [GitHub API Documentation](https://docs.github.com/en/rest)
- [JSONPlaceholder API](https://jsonplaceholder.typicode.com/)