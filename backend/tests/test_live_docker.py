import time
import json
import urllib.request


def http_post(url, data):
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


def http_get(url):
    with urllib.request.urlopen(url) as resp:
        return json.loads(resp.read().decode("utf-8"))


def run_smoke_test():
    print("--- 1. Testing GET /health on Backend & Frontend ---")
    b_health = http_get("http://localhost:8000/health")
    f_health = http_get("http://localhost:3000/health")
    assert b_health["status"] == "healthy"
    assert f_health["status"] == "healthy"
    print("Health checks OK:", b_health)

    print("--- 2. Testing POST /api/repositories ---")
    repo = http_post("http://localhost:8000/api/repositories", {
        "url": "https://github.com/octocat/Hello-World",
        "name": "octocat/Hello-World",
        "default_branch": "master"
    })
    repo_id = repo["id"]
    print(f"Created Repo: {repo['name']} (ID: {repo_id})")

    print("--- 3. Testing GET /api/repositories ---")
    repos = http_get("http://localhost:8000/api/repositories")
    assert any(r["id"] == repo_id for r in repos)
    print(f"Listed {len(repos)} repositories successfully.")

    print("--- 4. Testing POST /api/repositories/{id}/index ---")
    index_job = http_post(f"http://localhost:8000/api/repositories/{repo_id}/index", {"force_reindex": True})
    print("Dispatched Indexing Job:", index_job["status"])

    print("--- 5. Testing GET /api/repositories/{id}/status ---")
    status = http_get(f"http://localhost:8000/api/repositories/{repo_id}/status")
    print(f"Indexing Status: {status['status']} (Files: {status['indexed_files']}, Chunks: {status['total_chunks']})")

    print("--- 6. Testing POST /api/chat ---")
    chat_payload = {
        "repository_id": repo_id,
        "message": "Explain what this repository does and where hello world is printed"
    }
    chat_res = http_post("http://localhost:8000/api/chat", chat_payload)
    print("Chat Response received!")
    print("Message ID:", chat_res["message_id"])
    print("Answer excerpt:", chat_res["answer"][:200])
    print("Execution ID:", chat_res["execution_id"])
    print(f"Provider Used: {chat_res['trace']['provider_used']} | Model: {chat_res['trace']['model_used']} | Latency: {chat_res['trace']['latency_ms']}ms")
    print("Pipeline Steps:", [s["name"] for s in chat_res["trace"]["steps"]])

    print("--- 7. Testing GET /api/executions/{id} ---")
    trace = http_get(f"http://localhost:8000/api/executions/{chat_res['execution_id']}")
    assert trace["id"] == chat_res["execution_id"]
    print(f"Retrieved Execution Trace for query: '{trace['query']}'")

    print("\n>>> ALL LIVE DOCKER SERVICES VERIFIED END-TO-END! <<<")


if __name__ == "__main__":
    run_smoke_test()
