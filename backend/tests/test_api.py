import pytest


@pytest.mark.asyncio
async def test_health_endpoint(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["service"] == "RepoMind API"


@pytest.mark.asyncio
async def test_repository_lifecycle(client):
    # 1. Create repository
    payload = {
        "url": "https://github.com/octocat/Hello-World",
        "name": "octocat/Hello-World",
        "default_branch": "master"
    }
    resp = await client.post("/api/repositories", json=payload)
    assert resp.status_code == 201
    repo = resp.json()
    assert repo["name"] == "octocat/Hello-World"
    assert repo["status"] == "unindexed"
    repo_id = repo["id"]

    # 2. List repositories
    list_resp = await client.get("/api/repositories")
    assert list_resp.status_code == 200
    repos = list_resp.json()
    assert len(repos) >= 1
    assert any(r["id"] == repo_id for r in repos)

    # 3. Check status
    status_resp = await client.get(f"/api/repositories/{repo_id}/status")
    assert status_resp.status_code == 200
    assert status_resp.json()["repository_id"] == repo_id


@pytest.mark.asyncio
async def test_chat_flow(client):
    # 1. Create repo
    payload = {
        "url": "https://github.com/octocat/Spoon-Knife",
        "name": "octocat/Spoon-Knife",
        "default_branch": "main"
    }
    repo_res = await client.post("/api/repositories", json=payload)
    repo = repo_res.json()
    repo_id = repo["id"]

    # 2. Send chat request
    chat_payload = {
        "repository_id": repo_id,
        "message": "What is the purpose of this repository?"
    }
    chat_res = await client.post("/api/chat", json=chat_payload)
    assert chat_res.status_code == 200
    chat_data = chat_res.json()
    assert "answer" in chat_data
    assert len(chat_data["answer"]) > 0
    assert "trace" in chat_data
    assert chat_data["trace"]["query"] == chat_payload["message"]
    assert len(chat_data["trace"]["steps"]) > 0

    # 3. Fetch execution trace
    exec_id = chat_data["execution_id"]
    trace_res = await client.get(f"/api/executions/{exec_id}")
    assert trace_res.status_code == 200
    trace_data = trace_res.json()
    assert trace_data["id"] == exec_id
