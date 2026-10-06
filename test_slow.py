import asyncio
import time
import httpx

async def test_slow_inference():
    print("Starting test...")
    # Get a token
    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as client:
        # First register/login to get token
        login_data = {"email": "agentuser@example.com", "password": "password123"}
        try:
            resp = await client.post("/api/v1/auth/login", json=login_data)
        except Exception as e:
            print("Login error:", e)
            return
            
        if resp.status_code != 200:
            print("Could not login. Status:", resp.status_code, resp.text)
            print("Trying to register...")
            reg_resp = await client.post("/api/v1/auth/register", json={
                "email": "agentuser@example.com",
                "username": "agentuser",
                "password": "password123",
                "full_name": "Agent User"
            })
            print("Register response:", reg_resp.status_code, reg_resp.text)
            resp = await client.post("/api/v1/auth/login", json=login_data)
            print("Second login response:", resp.status_code, resp.text)
            
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Send chat request
        payload = {
            "thread_id": "real-test-thread",
            "message": "Create a detailed marketing campaign for an AI product. Include target audience, key messaging, and a multi-platform content strategy. This should take a while to generate.",
            "mode": "workflow"
        }
        
        print("Sending chat request...")
        start_time = time.time()
        chat_resp = await client.post("/api/v1/agent/chat", json=payload, headers=headers)
        elapsed = time.time() - start_time
        
        print(f"Chat POST returned in {elapsed:.3f} seconds with status {chat_resp.status_code}")
        data = chat_resp.json()
        print("Chat POST response:", data)
        
        if chat_resp.status_code != 202:
            print("Failed to get 202 status.")
            return
            
        job_id = data["job_id"]
        
        # Poll
        while True:
            poll_resp = await client.get(f"/api/v1/agent/jobs/{job_id}", headers=headers)
            poll_data = poll_resp.json()
            status = poll_data.get("status")
            print(f"Poll status: {status}")
            
            if status in ["completed", "failed", "approval_pending"]:
                print("Final result:", poll_data.get("result") or poll_data.get("error"))
                break
                
            await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(test_slow_inference())
