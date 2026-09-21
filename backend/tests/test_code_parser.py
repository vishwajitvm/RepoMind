import pytest
from app.services.code_parser import CodeParser, is_ignored_file, contains_secrets, detect_language


def test_detect_language():
    assert detect_language("app/main.py") == "python"
    assert detect_language("src/App.tsx") == "typescript"
    assert detect_language("service.go") == "go"
    assert detect_language("README.md") == "markdown"
    assert detect_language("unknown.xyz") == "unknown"


def test_is_ignored_file():
    assert is_ignored_file(".git/config") is True
    assert is_ignored_file("node_modules/react/index.js") is True
    assert is_ignored_file("dist/bundle.js") is True
    assert is_ignored_file("__pycache__/app.cpython-310.pyc") is True
    assert is_ignored_file(".env") is True
    assert is_ignored_file(".env.local") is True
    assert is_ignored_file("secrets.json") is True
    assert is_ignored_file("image.png") is True
    assert is_ignored_file("src/components/Button.tsx") is False
    assert is_ignored_file("backend/app/main.py") is False


def test_contains_secrets():
    assert contains_secrets("const token = 'ghp_1234567890abcdefghijklmnop';") is True
    assert contains_secrets("password = 'supersecretpassword123'") is True
    assert contains_secrets("def hello_world(): return 'hello'") is False


def test_python_code_parsing():
    sample_code = """\"\"\"Sample module docstring.\"\"\"

class UserService:
    def __init__(self, db):
        self.db = db

    def get_user(self, user_id: str):
        return self.db.find(user_id)

def calculate_metric(val: int) -> int:
    return val * 2
"""
    chunks = CodeParser.chunk_file("services/user_service.py", sample_code)
    assert len(chunks) >= 3

    symbols = [c.symbol for c in chunks]
    assert "UserService" in symbols
    assert "UserService.get_user" in symbols
    assert "calculate_metric" in symbols

    for c in chunks:
        assert c.path == "services/user_service.py"
        assert c.language == "python"
        assert c.start_line > 0
        assert c.end_line >= c.start_line
        assert len(c.content) > 0


def test_typescript_code_parsing():
    ts_code = """
export interface UserProfile {
    id: string;
    username: string;
}

export function formatUsername(user: UserProfile): string {
    return `@${user.username}`;
}
"""
    chunks = CodeParser.chunk_file("src/utils/user.ts", ts_code)
    assert len(chunks) >= 2
    symbols = [c.symbol for c in chunks]
    assert "UserProfile" in symbols
    assert "formatUsername" in symbols
