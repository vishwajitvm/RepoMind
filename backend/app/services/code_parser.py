import ast
import os
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class CodeChunk:
    path: str
    language: str
    symbol: Optional[str]
    chunk_type: str  # function, class, method, interface, type, module, block
    start_line: int
    end_line: int
    content: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "path": self.path,
            "language": self.language,
            "symbol": self.symbol,
            "chunk_type": self.chunk_type,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "content": self.content
        }


EXTENSION_LANGUAGE_MAP = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".go": "go",
    ".rs": "rust",
    ".java": "java",
    ".c": "c",
    ".cpp": "cpp",
    ".h": "c",
    ".hpp": "cpp",
    ".cs": "csharp",
    ".rb": "ruby",
    ".php": "php",
    ".sql": "sql",
    ".sh": "shell",
    ".bash": "shell",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".json": "json",
    ".md": "markdown"
}

IGNORED_DIRECTORIES = {
    ".git", "node_modules", "dist", "build", "coverage",
    ".venv", "venv", "env", "__pycache__", "vendor",
    ".idea", ".vscode", ".pytest_cache", "storybook-static"
}

IGNORED_EXTENSIONS = {
    ".pyc", ".pyo", ".pyd", ".so", ".dll", ".exe",
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico",
    ".mp4", ".mov", ".avi", ".mp3", ".wav",
    ".pdf", ".zip", ".tar", ".gz", ".7z", ".lock"
}

SECRET_PATTERNS = [
    re.compile(r"(?i)(?:password|passwd|secret|api[_-]?key|access[_-]?token|auth[_-]?token|token|private[_-]?key)\s*[:=]\s*['\"][^'\"]{8,}['\"]"),
    re.compile(r"ghp_[a-zA-Z0-9]{20,}"),
    re.compile(r"github_pat_[a-zA-Z0-9_]{22,}"),
    re.compile(r"(?i)-----BEGIN (?:RSA |EC )?PRIVATE KEY-----"),
]


def detect_language(file_path: str) -> str:
    _, ext = os.path.splitext(file_path.lower())
    return EXTENSION_LANGUAGE_MAP.get(ext, "unknown")


def is_ignored_file(file_path: str) -> bool:
    normalized = file_path.replace("\\", "/")
    parts = normalized.split("/")
    
    for part in parts:
        if part in IGNORED_DIRECTORIES:
            return True
            
    filename = parts[-1]
    
    if filename.startswith(".env") or "credential" in filename.lower() or "secret" in filename.lower():
        return True
        
    _, ext = os.path.splitext(filename.lower())
    if ext in IGNORED_EXTENSIONS:
        return True
        
    return False


def contains_secrets(content: str) -> bool:
    for pattern in SECRET_PATTERNS:
        if pattern.search(content):
            return True
    return False


class CodeParser:
    @classmethod
    def parse_python(cls, file_path: str, content: str) -> List[CodeChunk]:
        chunks: List[CodeChunk] = []
        lines = content.splitlines()

        try:
            tree = ast.parse(content, filename=file_path)
        except SyntaxError:
            return cls.parse_generic_blocks(file_path, content, "python")

        docstring = ast.get_docstring(tree)
        if docstring:
            chunks.append(CodeChunk(
                path=file_path,
                language="python",
                symbol="module_docstring",
                chunk_type="module",
                start_line=1,
                end_line=min(len(docstring.splitlines()) + 2, max(1, len(lines))),
                content=docstring
            ))

        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                start = node.lineno
                end = getattr(node, "end_lineno", start)
                class_content = "\n".join(lines[start - 1:end])
                chunks.append(CodeChunk(
                    path=file_path,
                    language="python",
                    symbol=node.name,
                    chunk_type="class",
                    start_line=start,
                    end_line=end,
                    content=class_content
                ))
                for sub in node.body:
                    if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        m_start = sub.lineno
                        m_end = getattr(sub, "end_lineno", m_start)
                        method_content = "\n".join(lines[m_start - 1:m_end])
                        chunks.append(CodeChunk(
                            path=file_path,
                            language="python",
                            symbol=f"{node.name}.{sub.name}",
                            chunk_type="method",
                            start_line=m_start,
                            end_line=m_end,
                            content=method_content
                        ))
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                start = node.lineno
                end = getattr(node, "end_lineno", start)
                func_content = "\n".join(lines[start - 1:end])
                chunks.append(CodeChunk(
                    path=file_path,
                    language="python",
                    symbol=node.name,
                    chunk_type="function",
                    start_line=start,
                    end_line=end,
                    content=func_content
                ))

        if not chunks:
            return cls.parse_generic_blocks(file_path, content, "python")

        return chunks

    @classmethod
    def parse_typescript_javascript(cls, file_path: str, content: str, language: str) -> List[CodeChunk]:
        chunks: List[CodeChunk] = []
        lines = content.splitlines()

        symbol_patterns = [
            (r"(?m)^(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s+([a-zA-Z0-9_$]+)", "function"),
            (r"(?m)^(?:export\s+)?class\s+([a-zA-Z0-9_$]+)", "class"),
            (r"(?m)^(?:export\s+)?interface\s+([a-zA-Z0-9_$]+)", "interface"),
            (r"(?m)^(?:export\s+)?type\s+([a-zA-Z0-9_$]+)\s*=", "type"),
            (r"(?m)^(?:export\s+)?const\s+([a-zA-Z0-9_$]+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>", "function"),
            (r"(?m)^(?:export\s+)?const\s+([a-zA-Z0-9_$]+)\s*:\s*React\.FC", "component"),
        ]

        found_positions = []
        for pat, chunk_type in symbol_patterns:
            for match in re.finditer(pat, content):
                symbol_name = match.group(1)
                start_char = match.start()
                start_line = content[:start_char].count("\n") + 1
                found_positions.append((start_line, symbol_name, chunk_type))

        found_positions.sort(key=lambda x: x[0])

        if not found_positions:
            return cls.parse_generic_blocks(file_path, content, language)

        for i, (start_line, symbol_name, chunk_type) in enumerate(found_positions):
            if i < len(found_positions) - 1:
                next_start = found_positions[i + 1][0]
                end_line = max(start_line, next_start - 1)
            else:
                end_line = len(lines)
            chunk_content = "\n".join(lines[start_line - 1:end_line])
            chunks.append(CodeChunk(
                path=file_path,
                language=language,
                symbol=symbol_name,
                chunk_type=chunk_type,
                start_line=start_line,
                end_line=end_line,
                content=chunk_content
            ))

        return chunks

    @classmethod
    def parse_generic_blocks(cls, file_path: str, content: str, language: str, max_lines: int = 60) -> List[CodeChunk]:
        chunks: List[CodeChunk] = []
        lines = content.splitlines()
        total_lines = len(lines)

        if total_lines == 0:
            return chunks

        if total_lines <= max_lines:
            chunks.append(CodeChunk(
                path=file_path,
                language=language,
                symbol=None,
                chunk_type="module",
                start_line=1,
                end_line=total_lines,
                content=content
            ))
            return chunks

        i = 0
        block_idx = 1
        while i < total_lines:
            chunk_end = min(i + max_lines, total_lines)
            chunk_content = "\n".join(lines[i:chunk_end])
            chunks.append(CodeChunk(
                path=file_path,
                language=language,
                symbol=f"block_{block_idx}",
                chunk_type="block",
                start_line=i + 1,
                end_line=chunk_end,
                content=chunk_content
            ))
            block_idx += 1
            i = chunk_end

        return chunks

    @classmethod
    def chunk_file(cls, file_path: str, content: str) -> List[CodeChunk]:
        if contains_secrets(content):
            return []

        language = detect_language(file_path)

        if language == "python":
            return cls.parse_python(file_path, content)
        elif language in ("typescript", "javascript"):
            return cls.parse_typescript_javascript(file_path, content, language)
        else:
            return cls.parse_generic_blocks(file_path, content, language)
