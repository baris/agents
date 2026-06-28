---
name: sandbox_python_executor
description: Executes Python code snippets inside a highly restricted gVisor container sandbox.
---

# Sandbox Python Executor Skill

This skill provides secure, sandboxed execution of Python script execution blocks using gVisor containment.

## Constraints
- Memory Limit: 128MB
- CPU Quota: 1.0 core
- Timeout: 30 seconds
- Read-only root filesystem with writable `/tmp/scratch/` `tmpfs` volume.
- Network Access: Disabled (`--network none`)
