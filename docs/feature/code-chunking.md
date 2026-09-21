# Feature: Code-Aware Semantic Chunking

## 1. Overview (In Plain Language)

When standard search engines or simple AI tools read code, they often treat code like ordinary prose, cutting it into arbitrary 1,000-character blocks. This is disastrous for code because a function header might end up in one chunk while the function body ends up in another, destroying the logic.

RepoMind uses **Code-Aware Semantic Chunking**:
- It reads the code using the programming language's actual grammar rules.
- It identifies complete logical units—such as an entire Python class, a React component, or a TypeScript interface.
- It tracks the exact line numbers (e.g. lines 45 to 82) so you can always locate the exact source code.

---

## 2. Code Chunking Pipeline Diagram

![Code-Aware Semantic Chunking Pipeline](https://mermaid.ink/svg/Zmxvd2NoYXJ0IFRECiAgICBSYXdDb2RlW1JhdyBTb3VyY2UgRmlsZV0gLS0+IExhbmdEZXRlY3R7RGV0ZWN0IExhbmd1YWdlfQogICAgCiAgICBMYW5nRGV0ZWN0IC0tPnxQeXRob24gLnB5fCBQeXRob25BU1RbUHl0aG9uIEFTVCBQYXJzZXI6IGFzdC5wYXJzZV0KICAgIExhbmdEZXRlY3QgLS0+fFR5cGVTY3JpcHQgLyBKYXZhU2NyaXB0IC50cy8udHN4Ly5qc3wgUmVnZXhQYXJzZXJbU3ltYm9sIEV4dHJhY3RvcjogY2xhc3NlcywgZnVuY3Rpb25zLCB0eXBlc10KICAgIExhbmdEZXRlY3QgLS0+fEdvIC8gUnVzdCAvIEphdmF8IE11bHRpTGFuZ1BhcnNlcltCbG9jayAmIEluZGVudGF0aW9uIFBhcnNlcl0KICAgIAogICAgUHl0aG9uQVNUIC0tPiBFeHRyYWN0UHlbRXh0cmFjdCBDbGFzc2VzLCBNZXRob2RzLCBGdW5jdGlvbnMsIERvY3N0cmluZ3NdCiAgICBSZWdleFBhcnNlciAtLT4gRXh0cmFjdFRTW0V4dHJhY3QgQ29tcG9uZW50cywgSW50ZXJmYWNlcywgRXhwb3J0ZWQgU3ltYm9sc10KICAgIE11bHRpTGFuZ1BhcnNlciAtLT4gRXh0cmFjdEJsb2Nrc1tFeHRyYWN0IExvZ2ljYWwgU2NvcGVzICYgTGluZSBTcGFuc10KICAgIAogICAgRXh0cmFjdFB5IC0tPiBDaHVua1BheWxvYWRbU3RydWN0dXJlZCBDb2RlIENodW5rcyArIExpbmUgUmFuZ2VzICsgTWV0YWRhdGFdCiAgICBFeHRyYWN0VFMgLS0+IENodW5rUGF5bG9hZAogICAgRXh0cmFjdEJsb2NrcyAtLT4gQ2h1bmtQYXlsb2Fk)

```mermaid
flowchart TD
    RawCode[Raw Source File] --> LangDetect{Detect Language}
    
    LangDetect -->|Python .py| PythonAST[Python AST Parser: ast.parse]
    LangDetect -->|TypeScript / JavaScript .ts/.tsx/.js| RegexParser[Symbol Extractor: classes, functions, types]
    LangDetect -->|Go / Rust / Java| MultiLangParser[Block & Indentation Parser]
    
    PythonAST --> ExtractPy[Extract Classes, Methods, Functions, Docstrings]
    RegexParser --> ExtractTS[Extract Components, Interfaces, Exported Symbols]
    MultiLangParser --> ExtractBlocks[Extract Logical Scopes & Line Spans]
    
    ExtractPy --> ChunkPayload[Structured Code Chunks + Line Ranges + Metadata]
    ExtractTS --> ChunkPayload
    ExtractBlocks --> ChunkPayload
```

---

## 3. Technical Architecture & Implementation

### 3.1 Python Abstract Syntax Tree (AST) Parsing
For Python files, RepoMind uses Python's standard `ast` module:
- Parses `ast.ClassDef`, `ast.FunctionDef`, and `ast.AsyncFunctionDef`.
- Preserves method hierarchy (`ClassName.method_name`).
- Extracts module-level docstrings as distinct architectural overview chunks.
- Preserves original indentation and exact 1-indexed `start_line` and `end_line`.

### 3.2 TypeScript / JavaScript Parsing
For JavaScript and TypeScript files:
- Detects `interface`, `type`, `class`, `export function`, and `React.FC` components.
- Scopes function boundaries using brace balancing and regex symbol detection.

### 3.3 Chunk Payload Metadata Schema
Every chunk emitted by the parser is enriched with metadata before vectorization:
```json
{
  "path": "app/services/orchestrator.py",
  "language": "python",
  "symbol": "LangGraphOrchestrator.run",
  "chunk_type": "method",
  "start_line": 142,
  "end_line": 188,
  "repository_id": "cbee282e-bad2-4603-b556-9256fddf1b2f"
}
```
