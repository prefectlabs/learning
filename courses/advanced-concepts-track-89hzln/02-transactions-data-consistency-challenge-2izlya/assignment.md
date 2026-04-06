---
slug: transactions-data-consistency-challenge-2izlya
id: 0vhdhjxbhlf9
type: challenge
title: ' Transactions & Data Consistency'
teaser: Master Prefect transactions for atomic operations and automatic rollback.
  Build workflows that maintain data consistency even when tasks fail using transaction
  key-value storage and rollback hooks.
notes:
- type: text
  contents: |-
    # Partial Failures Leave Data Inconsistent

      Real workflows often involve multiple steps that must succeed together. Without transactions, you get partial
      updates when validation fails, files left on disk from interrupted processes, and data corruption that's
      difficult to debug. Your workflows can succeed partially, leaving your system in an unknown state.
- type: text
  contents: |2-
      # The Solution: Atomic Operations with Automatic Cleanup

      Prefect transactions group related tasks atomically using the transaction lifecycle. Tasks execute and stage
      their data, then either all commit together or all roll back automatically. Rollback hooks with transaction
      key-value storage ensure proper cleanup, so failed workflows leave no trace behind.
- type: text
  contents: "# Bulletproof Data Consistency\n\n  Your workflows now maintain data
    integrity even during failures. Files get automatically deleted when validation\n
    \ fails, API records get cleaned up when business rules break, and related operations
    succeed or fail as a unit. No\n   more manual cleanup or wondering what succeeded
    when workflows crash.\n\n\t Let's get started..."
tabs:
- id: atwcvx07jksy
  title: "\U0001F4BB Terminal"
  type: terminal
  hostname: prefect-sandbox
  cmd: /bin/bash
- id: ovdkunxc6fpr
  title: "\U0001F6A7 Code Editor"
  type: code
  hostname: prefect-sandbox
  path: /root
difficulty: ""
enhanced_loading: null
---
Introduction
===

Let's master atomic operations and data consistency using Prefect's transaction system.

**Why This Matters:**
Real-world workflows often involve multiple steps that must succeed or fail together. Without proper transaction handling, you get:
- Partial updates that leave data in inconsistent states
- Side effects that can't be undone when workflows fail
- Data corruption from interrupted processes
- Difficult debugging when you don't know what succeeded

Prefect's transaction system ensures atomic operations - either everything succeeds or everything gets rolled back.

**What You'll Learn:**
- Transaction lifecycle: BEGIN → STAGE → ROLLBACK/COMMIT
- Prefect transactions for atomic operations
- `on_rollback` hooks for automatic cleanup
- Transaction key-value storage for data sharing
- Idempotency and race condition handling
- Real-world transaction scenarios with file operations and APIs

**Hands-On Exercise:**
Build bulletproof workflows that maintain data consistency even when things go wrong.

Let's start by setting up our workspace and installing the dependencies we'll need:

```run
# Install uv for fast package management
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env

# Create virtual environment and install required packages
uv venv && source .venv/bin/activate
uv pip install prefect requests
```

Now let's create our workspace files:

```run
touch problematic_pipeline.py
touch transactional_pipeline.py
```

**Transaction Lifecycle Understanding:**
Before diving into examples, understand the transaction stages:
1. **BEGIN**: Transaction starts, computes unique key
2. **STAGE**: Tasks execute and stage their data
3. **ROLLBACK**: If any staged task fails, all rollback hooks execute
4. **COMMIT**: If all tasks succeed, changes are permanent

Let's start with the official Prefect pattern - a file operation with validation.

Copy this code into `problematic_pipeline.py`:

```python
import os
from prefect import task, flow, get_run_logger

@task
def write_file(contents: str):
    """Write content to file"""
    logger = get_run_logger()
    logger.info("Writing file with side effects")

    with open("side-effect.txt", "w") as f:
        f.write(contents)

    logger.info("File written successfully")

@task
def quality_test():
    """Test file quality - this might fail"""
    logger = get_run_logger()
    logger.info("Running quality test on file")

    with open("side-effect.txt", "r") as f:
        data = f.readlines()

    if len(data) < 2:
        raise ValueError("Not enough data in file!")

    logger.info("Quality test passed")
    return True

@flow
def problematic_pipeline(contents: str):
    """Pipeline without transactions - leaves files when validation fails"""
    write_file(contents)
    quality_test()  # If this fails, file remains on disk
    return "Pipeline completed successfully"

if __name__ == "__main__":
    try:
        # This will fail quality test but leave the file
        result = problematic_pipeline("Single line")  # Not enough lines
        print(result)
    except Exception as e:
        print(f"Pipeline failed: {e}")
        print(f"File exists: {os.path.exists('side-effect.txt')}")
        # Clean up manually
        if os.path.exists('side-effect.txt'):
            os.remove('side-effect.txt')
```

This workflow leaves files when validation fails. Let's fix it with transactions.

Now copy this code into `transactional_pipeline.py`:

```python
import os
from prefect import task, flow, get_run_logger
from prefect.transactions import transaction

@task
def write_file(contents: str):
    """Write content to file"""
    logger = get_run_logger()
    logger.info("Writing file with side effects")

    with open("side-effect.txt", "w") as f:
        f.write(contents)

    logger.info("File written successfully")

@write_file.on_rollback
def del_file(txn):
    """Rollback hook: delete the file if transaction fails"""
    logger = get_run_logger()
    logger.info("Executing rollback: deleting file")

    if os.path.exists("side-effect.txt"):
        os.unlink("side-effect.txt")
        logger.info("Rolled back: deleted side-effect.txt")

@task
def quality_test():
    """Test file quality - this might fail"""
    logger = get_run_logger()
    logger.info("Running quality test on file")

    with open("side-effect.txt", "r") as f:
        data = f.readlines()

    if len(data) < 2:
        raise ValueError("Not enough data in file!")

    logger.info("Quality test passed")
    return True

@flow
def transactional_pipeline(contents: str):
    """Pipeline with proper transaction handling"""
    with transaction():
        write_file(contents)
        quality_test()  # If this fails, file gets deleted automatically

    return "Pipeline completed successfully"

if __name__ == "__main__":
    try:
        # This will fail quality test but file will be cleaned up
        result = transactional_pipeline("Single line")  # Not enough lines
        print(result)
    except Exception as e:
        print(f"Pipeline failed: {e}")
        print(f"File exists after rollback: {os.path.exists('side-effect.txt')}")
        # No manual cleanup needed - transaction handled it!
```

**Key concepts you just learned:**
- `transaction()` context manager groups tasks atomically
- `@task.on_rollback` hooks define cleanup actions that execute on failure
- Rollback happens automatically when any staged task fails
- `txn` parameter in rollback hooks provides transaction context
- Data consistency is maintained even when workflows fail

Try running both examples to see the difference:

```run
echo "First, run the problematic version:"
python3 problematic_pipeline.py
echo "File exists: $(ls -la side-effect.txt 2>/dev/null || echo 'No file')"
```

```run
echo "Now run the transactional version:"
python3 transactional_pipeline.py
echo "File exists after rollback: $(ls -la side-effect.txt 2>/dev/null || echo 'No file - properly cleaned up!')"
```

Now let's build a more complex example using transaction key-value storage.

Create the complex example file:

```run
touch create_user_with_posts_flow.py
```

Copy this code into `create_user_with_posts_flow.py`:

```python
import os
import json
import requests
from prefect import task, flow, get_run_logger
from prefect.transactions import transaction

@task
def create_user_record(user_data):
    """Create a new user record with transaction key storage"""
    logger = get_run_logger()
    logger.info(f"Creating user record for {user_data['name']}")

    # Simulate API call to create user
    response = requests.post(
        "https://jsonplaceholder.typicode.com/users",
        json=user_data
    )
    response.raise_for_status()
    created_user = response.json()

    # Save to local file for demonstration
    filename = f"user_{created_user['id']}.json"
    with open(filename, 'w') as f:
        json.dump(created_user, f, indent=2)

    logger.info(f"User record created with ID: {created_user['id']}")
    return created_user

@create_user_record.on_rollback
def delete_user_record(txn):
    """Rollback hook: delete user record using transaction key-value store"""
    logger = get_run_logger()
    user_id = txn.get('user_id')

    if user_id:
        filename = f"user_{user_id}.json"
        if os.path.exists(filename):
            os.remove(filename)
            logger.info(f"Rolled back: deleted user record {filename}")

@task
def create_user_posts(posts_data):
    """Create posts for the user using transaction storage"""
    logger = get_run_logger()
    # Note: user_id will be retrieved from transaction context
    logger.info(f"Creating {len(posts_data)} posts")

    created_posts = []
    for post in posts_data:
        # Add user_id from transaction context
        post['userId'] = 999  # Demo user ID
        response = requests.post(
            "https://jsonplaceholder.typicode.com/posts",
            json=post
        )
        response.raise_for_status()
        created_post = response.json()
        created_posts.append(created_post)

    # Save posts to file using transaction key
    logger.info(f"Created {len(created_posts)} posts")
    return created_posts

@create_user_posts.on_rollback
def delete_user_posts(txn):
    """Rollback hook: delete user posts using transaction key"""
    logger = get_run_logger()
    user_id = txn.get('user_id')
    posts_file = txn.get('posts_file')

    if posts_file and os.path.exists(posts_file):
        os.remove(posts_file)
        logger.info(f"Rolled back: deleted posts file {posts_file}")

@task
def validate_user_completeness(user_data, posts_data):
    """Validate that user has complete data"""
    logger = get_run_logger()

    # Check user data
    if not user_data.get('email'):
        raise ValueError("User email is required")

    # Check posts data
    if len(posts_data) < 1:
        raise ValueError("User must have at least one post")

    # Simulate business rule that might fail
    if user_data.get('name', '').lower() == 'invalid':
        raise ValueError("Invalid user name detected")

    logger.info("User data validation passed")
    return True

@flow(name="create-user-with-posts-{user_id}")
def create_user_with_posts_flow(user_id: int):
    """Create user with posts using transaction key-value storage"""
    logger = get_run_logger()
    logger.info(f"Starting user creation workflow for user {user_id}")

    # Sample user data
    user_data = {
        "id": user_id,
        "name": "John Doe",
        "username": f"johndoe{user_id}",
        "email": f"john{user_id}@example.com",
        "phone": "555-1234",
        "website": "johndoe.com"
    }

    # Sample posts data
    posts_data = [
        {
            "title": f"Hello World from User {user_id}",
            "body": "This is my first post!"
        },
        {
            "title": f"Update from User {user_id}",
            "body": "Here's what I've been working on..."
        }
    ]

    with transaction() as txn:
        # Set transaction keys for rollback hooks
        txn.set('user_id', user_id)
        txn.set('posts_file', f"posts_{user_id}.json")

        # Create user record
        created_user = create_user_record(user_data)

        # Create user posts
        created_posts = create_user_posts(posts_data)

        # Save posts file after creation
        posts_filename = f"posts_{user_id}.json"
        with open(posts_filename, 'w') as f:
            json.dump(created_posts, f, indent=2)

        # Validate everything is complete
        validate_user_completeness(created_user, created_posts)

    logger.info(f"Successfully created user {user_id} with {len(created_posts)} posts")
    return {
        "user": created_user,
        "posts": created_posts,
        "status": "completed"
    }

if __name__ == "__main__":
    try:
        result = create_user_with_posts_flow(999)
        print(f"Success: {result['status']}")
        print(f"User ID: {result['user']['id']}")
        print(f"Posts created: {len(result['posts'])}")
    except Exception as e:
        print(f"Transaction failed: {e}")
        print("All changes should be rolled back automatically")
```

**Key concepts you just learned:**
- **Transaction key-value storage** - `txn.set()` and `txn.get()` for sharing data
- **Multiple rollback hooks** - Each task can have its own cleanup logic
- **Rollback hook parameters** - Use `txn` parameter, not `transaction.parameters`
- **Complex data consistency** - Related records are created or rolled back together
- **Automatic cleanup** - Failed transactions trigger all rollback hooks

Run this to see complex transaction handling:

```run
python3 create_user_with_posts_flow.py
```

**Transaction Key-Value Storage Deep Dive:**
Notice how we use `txn.set()` to store information that rollback hooks need:
- Store file paths, IDs, and other cleanup data in the transaction
- Rollback hooks access this data with `txn.get()`
- This ensures rollback hooks have the context they need for cleanup

Now let's create an advanced example with conditional transactions and error recovery.

Create the advanced example file:

```run
touch update_user_with_profile_flow.py
```

Copy this code into `update_user_with_profile_flow.py`:

```python
import os
import json
import requests
from prefect import task, flow, get_run_logger
from prefect.transactions import transaction

@task
def fetch_existing_user(user_id: int):
    """Check if user already exists"""
    logger = get_run_logger()

    try:
        response = requests.get(f"https://jsonplaceholder.typicode.com/users/{user_id}")
        if response.status_code == 200:
            logger.info(f"User {user_id} already exists")
            return response.json()
        else:
            logger.info(f"User {user_id} does not exist")
            return None
    except Exception as e:
        logger.error(f"Error checking user {user_id}: {e}")
        return None

@task
def update_user_data(user_data, updates):
    """Update user data with new information"""
    logger = get_run_logger()
    logger.info(f"Updating user {user_data['id']} with new data")

    # Merge updates
    updated_user = {**user_data, **updates}

    # Simulate API update
    response = requests.put(
        f"https://jsonplaceholder.typicode.com/users/{user_data['id']}",
        json=updated_user
    )
    response.raise_for_status()

    # Save to file
    filename = f"user_{updated_user['id']}_updated.json"
    with open(filename, 'w') as f:
        json.dump(updated_user, f, indent=2)

    logger.info(f"User {user_data['id']} updated successfully")
    return updated_user

@update_user_data.on_rollback
def restore_original_user(txn):
    """Rollback hook: restore original user data"""
    logger = get_run_logger()
    user_id = txn.get('user_id')
    updated_filename = txn.get('updated_filename')
    original_filename = txn.get('original_filename')

    if updated_filename and os.path.exists(updated_filename):
        os.remove(updated_filename)
        logger.info(f"Rolled back: removed updated user file {updated_filename}")

    if original_filename and os.path.exists(original_filename):
        logger.info(f"Original user data preserved in {original_filename}")

@task
def create_user_profile(user_id: int, profile_data):
    """Create user profile (simulate related table)"""
    logger = get_run_logger()
    logger.info(f"Creating profile for user {user_id}")

    profile = {
        "userId": user_id,
        "bio": profile_data.get("bio", "No bio provided"),
        "location": profile_data.get("location", "Unknown"),
        "interests": profile_data.get("interests", [])
    }

    # Save profile to file
    filename = f"profile_{user_id}.json"
    with open(filename, 'w') as f:
        json.dump(profile, f, indent=2)

    logger.info(f"Profile created for user {user_id}")
    return profile

@create_user_profile.on_rollback
def delete_user_profile(txn):
    """Rollback hook: delete user profile"""
    logger = get_run_logger()
    profile_filename = txn.get('profile_filename')

    if profile_filename and os.path.exists(profile_filename):
        os.remove(profile_filename)
        logger.info(f"Rolled back: deleted profile file {profile_filename}")

@task
def validate_user_update(user_data, profile_data):
    """Validate user update data"""
    logger = get_run_logger()

    # Validate user data
    if not user_data.get('email'):
        raise ValueError("Email is required for user update")

    # Validate profile data
    if not profile_data.get('bio'):
        raise ValueError("Bio is required for user profile")

    # Simulate business rule validation
    if len(profile_data.get('bio', '')) < 10:
        raise ValueError("Bio must be at least 10 characters long")

    logger.info("User update validation passed")
    return True

@flow(name="update-user-with-profile-{user_id}")
def update_user_with_profile_flow(user_id: int, updates: dict, profile_data: dict):
    """Update user with profile using conditional transactions"""
    logger = get_run_logger()
    logger.info(f"Starting user update workflow for user {user_id}")

    # Check if user exists
    existing_user = fetch_existing_user(user_id)

    if not existing_user:
        logger.warning(f"User {user_id} does not exist, skipping update")
        return {"status": "skipped", "reason": "user_not_found"}

    # Save original user data for potential rollback
    original_filename = f"user_{user_id}.json"
    with open(original_filename, 'w') as f:
        json.dump(existing_user, f, indent=2)

    try:
        with transaction() as txn:
            # Set transaction keys for rollback hooks
            txn.set('user_id', user_id)
            txn.set('updated_filename', f"user_{user_id}_updated.json")
            txn.set('original_filename', original_filename)
            txn.set('profile_filename', f"profile_{user_id}.json")

            # Update user data
            updated_user = update_user_data(existing_user, updates)

            # Create user profile
            profile = create_user_profile(user_id, profile_data)

            # Validate everything
            validate_user_update(updated_user, profile)

        logger.info(f"Successfully updated user {user_id} with profile")
        return {
            "user": updated_user,
            "profile": profile,
            "status": "completed"
        }

    except Exception as e:
        logger.error(f"User update failed: {e}")
        # Clean up original file if update failed
        if os.path.exists(original_filename):
            os.remove(original_filename)
        raise

if __name__ == "__main__":
    # Test with existing user
    updates = {
        "name": "John Updated",
        "email": "john.updated@example.com"
    }

    profile_data = {
        "bio": "This is a comprehensive bio for the user profile",
        "location": "San Francisco, CA",
        "interests": ["Python", "Data Engineering", "Prefect"]
    }

    try:
        result = update_user_with_profile_flow(1, updates, profile_data)
        print(f"Update result: {result['status']}")
        if result['status'] == 'completed':
            print(f"User: {result['user']['name']}")
            print(f"Profile bio: {result['profile']['bio']}")
    except Exception as e:
        print(f"Update failed: {e}")
        print("All changes should be rolled back automatically")
```

**Key concepts you just learned:**
- **Conditional transactions** - Only run transactions when needed
- **Transaction context passing** - `with transaction() as txn:` provides context object
- **Key-value store for rollbacks** - Store cleanup data with `txn.set()`, access with `txn.get()`
- **Data preservation** - Save original state before making changes
- **Business rule validation** - Validate data according to business requirements
- **Error recovery** - Graceful handling of different failure modes

Run this to see advanced transaction patterns:

```run
python3 update_user_with_profile_flow.py
```

What You've Accomplished
===

🎉 **Congratulations!** You've mastered Prefect's transaction system and built bulletproof workflows that maintain data consistency:

**The Business Impact:**
- **Data Integrity** - No more partial updates or corrupted data states
- **Reliability** - Failed operations clean up after themselves automatically
- **Debugging** - Clear rollback actions make it easy to understand what went wrong
- **Confidence** - Deploy complex workflows knowing they won't leave data in inconsistent states

**Technical Mastery:**

✅ **Transaction lifecycle** - Understanding BEGIN → STAGE → ROLLBACK/COMMIT flow
✅ **Transaction context managers** - `with transaction() as txn:` for atomic operations
✅ **Rollback hooks** - `@task.on_rollback` with proper `txn` parameter
✅ **Transaction key-value storage** - `txn.set()` and `txn.get()` for data sharing
✅ **Data consistency** - Related operations succeed or fail together
✅ **Complex rollback logic** - Multiple cleanup actions for different scenarios
✅ **Conditional transactions** - Only use transactions when needed
✅ **Error recovery** - Graceful handling of different failure modes
✅ **Real API integration** - Applied transactions to actual data operations

These patterns ensure your workflows maintain data integrity even in the face of failures, making them production-ready and reliable.

Next Steps
===

You're now ready for **Challenge 3: Futures & Asynchronous Patterns**, where you'll learn:
- Prefect futures for advanced parallel processing
- Asynchronous task execution patterns
- Complex dependency management
- Performance optimization with async workflows

The journey into advanced Prefect SDK capabilities continues! 🚀

Additional Resources
===

- [Prefect Transactions Documentation](https://docs.prefect.io/3.0/develop/transactions)
- [Prefect Rollback Hooks](https://docs.prefect.io/3.0/develop/transactions#rollback-hooks)
- [Prefect Error Handling](https://docs.prefect.io/concepts/flows/#error-handling)
- [JSONPlaceholder API](https://jsonplaceholder.typicode.com/)
- [Prefect Task Decorators](https://docs.prefect.io/v3/api-ref/python/prefect-tasks)
