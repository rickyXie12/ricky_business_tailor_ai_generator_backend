#
# test_performance.py
#
# This script tests your LIVE API endpoints.
# It does NOT import any of your application's internal code.
#
import requests
import time
import os

# --- Configuration ---
API_URL = "http://localhost:8000/api"

# ❗️ IMPORTANT: You must get a real campaign_id from your database for this to work.
# After you create a user and a campaign, copy the campaign's UUID and paste it here.
TEST_CAMPAIGN_ID = "029db4f1-3d4a-4738-8e75-d1b6c5e757e7"
# --------------------

# Add your test user credentials here
TEST_USERNAME = "ricky"
TEST_PASSWORD = "ricky"

def get_access_token(username: str, password: str) -> str:
    response = requests.post(
        f"{API_URL}/auth/login",
        data={"username": username, "password": password}
    )
    response.raise_for_status()
    return response.json()["access_token"]

def run_perf_test(num_posts: int):
    """Sends a request to the running API and polls for the result."""
    print(f"\n--- 🚀 Starting Performance Test: {num_posts} Posts ---")

    if "paste-your-real-campaign-uuid-here" in TEST_CAMPAIGN_ID:
        print("❌ ERROR: Please update the TEST_CAMPAIGN_ID variable in this script before running.")
        return

    # 0. Get access token
    token = get_access_token(TEST_USERNAME, TEST_PASSWORD)
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Prepare the request payload
    posts_data = [{
        'title': f'Perf Test Post #{i+1}',
        'topic': 'API Performance',
        'brief': f'This is a brief for performance test post number {i+1}.',
        'brand_name': 'Test Brand',
        'tone': 'professional',
        'target_audience': 'general audience'
    } for i in range(num_posts)]
    batch_request = {"name": f"API Test - {num_posts} posts", "posts": posts_data}

    # 2. Start the timer and send the request
    start_time = time.time()
    try:
        print(f"Sending POST request to {API_URL}/campaigns/{TEST_CAMPAIGN_ID}/generate-batch")
        response = requests.post(
            f"{API_URL}/campaigns/{TEST_CAMPAIGN_ID}/generate-batch",
            json=batch_request,
            headers=headers
        )
        response.raise_for_status()  # Raise an error for bad status codes (like 404 or 500)
    except requests.RequestException as e:
        print(f"❌ Error starting batch job: {e}")
        print(f"   Response body: {response.text if 'response' in locals() else 'No response'}")
        return

    job_id = response.json()['job_id']
    print(f"✅ Batch job started with ID: {job_id}")

    # 3. Poll the status endpoint until the job is complete
    while True:
        try:
            status_response = requests.get(
                f"{API_URL}/batch-jobs/{job_id}/status",
                headers=headers
            )
            status_response.raise_for_status()
            status_data = status_response.json()
            status = status_data['status']
            progress = status_data['progress']

            print(
                f"  -> Status: {status}, "
                f"Progress: {progress['completed']}/{progress['total']} "
                f"({progress['percentage']}%), "
                f"Failed: {progress['failed']}"
            )
            if status == 'completed' or status == 'failed':
                break
            
            time.sleep(5) # Wait 5 seconds between checks
        except requests.RequestException as e:
            print(f"❌ Error checking status: {e}")
            break

    end_time = time.time()
    duration = end_time - start_time
    
    print("-" * 30)
    print(f"✅ Batch of {num_posts} posts completed in {duration:.2f} seconds.")
    print("-" * 30)

if __name__ == "__main__":
    print("--- ⚠️  Make sure your FastAPI server is running in another terminal! ---")
    print("--- (uvicorn main:app --reload) ---")
    # run_perf_test(10) # Test with 10 posts
    run_perf_test(50) # Uncomment to test with 50
    # run_perf_test(100) # Uncomment to test with 100