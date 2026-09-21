# Feature: Resumable Repository Indexing

## Purpose
Enables developers to index remote GitHub repositories and local directories safely without blocking the application or risking catastrophic failure on corrupted or unsupported files.

## Key Capabilities
- **Shallow Clone Ingestion**: Clones `--depth 1` for the specified branch into a sandbox tempdir.
- **Strict File Filtering**: Ignores `.git`, `node_modules`, `dist`, `__pycache__`, media files, binaries, and secrets (`.env`, private keys, access tokens).
- **Asynchronous Processing**: HTTP requests enqueue jobs into Redis; the background worker consumes and processes the repository.
- **Resumable Error Boundaries**: Every file is processed individually; a single syntax error or embedding failure marks that file record as failed in PostgreSQL without stopping the rest of the job.
- **Real-Time Status**: The frontend polls `GET /api/repositories/{id}/status` to track `indexed_files`, `failed_files`, and `total_chunks`.
