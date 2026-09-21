# Feature: Code-Aware Semantic Chunking

## Purpose
Replaces naive fixed-character chunking (`text[i:i+1000]`) with semantic boundary parsing to ensure vector embeddings represent complete logical symbols.

## Implementation Details
- **Python**: Uses Python standard `ast` parsing to identify module docstrings, `ClassDef`, `FunctionDef`, and `AsyncFunctionDef` with inner method symbols (`Class.method`).
- **TypeScript/JavaScript**: Employs symbol regex extraction for `export function`, `class`, `interface`, `type`, and `React.FC` components.
- **Generic Fallbacks**: Bounded block chunking with line preservation.
- **Metadata Captured**:
  - `path`: relative file location
  - `language`: detected source language
  - `symbol`: symbol name or identifier
  - `chunk_type`: `class`, `function`, `method`, `interface`, `type`, `module`, `block`
  - `start_line` & `end_line`: exact 1-indexed line numbers
