# Actionable Antigravity Optimization Checklist

This document provides a production-grade checklist and configuration guidelines to align the workspace's Antigravity environment with optimal agent harness architectural patterns.

---

## 1. Global Workspace Rules (`AGENTS.md`)

*   **Status**: Integrated
*   **Target File**: `/Users/tbmetin/repos/agents/AGENTS.md`
*   **Action**: Integrated sandbox isolation rules into the workspace rule book:

```markdown
### Rule [AGENTS_SANDBOX_VERIFICATION]: Isolated Execution Boundaries
- **Runtime Enclosure**: All agent-generated code must execute inside a containerized sandbox runtime (e.g., Docker running with `gvisor` runtime, or a WebAssembly stack-based VM).
- **Resource Constraints**:
  - Memory limit: Max 128MB.
  - CPU quota: Max 1.0 core.
  - Timeout: Hard execution stop at 30 seconds.
- **Filesystem Security**: Mount root filesystem as read-only. Provide a dedicated writable scratch directory (`/tmp/scratch/`) mounted as a temporary `tmpfs` volume.
- **Network Boundary**: Disable host network access (`--network none`) for code execution sandboxes.
```

---

## 2. Customizations & Skills

*   **Status**: Created
*   **Target Directory**: `/Users/tbmetin/.agents/skills/sandbox_python_executor/`
*   **Action**: Created `SKILL.md` manifest for the Python Sandboxed Executor skill:

```markdown
---
name: sandbox_python_executor
description: Executes Python code snippets inside a highly restricted gVisor container sandbox.
---

# Sandbox Python Executor Skill
This skill provides secure, sandboxed execution of Python script execution blocks using gVisor containment.
```

---

## 3. Memory & State Persistence

*   **Status**: Reference Design
*   **Action**: Local key-value session persistence layer template using Go/BoltDB:

```go
package memory

import (
	"encoding/json"
	"fmt"
	"time"

	bolt "go.etcd.io/bbolt"
)

type SessionState struct {
	SessionID  string                 `json:"session_id"`
	UpdatedAt  time.Time              `json:"updated_at"`
	ActiveGoal string                 `json:"active_goal"`
	StepCount  int                    `json:"step_count"`
	Variables  map[string]interface{} `json:"variables"`
}

type BoltSessionStore struct {
	db         *bolt.DB
	bucketName []byte
}

func NewBoltSessionStore(dbPath string) (*BoltSessionStore, error) {
	db, err := bolt.Open(dbPath, 0600, &bolt.Options{Timeout: 1 * time.Second})
	if err != nil {
		return nil, fmt.Errorf("failed to open BoltDB: %w", err)
	}

	bucketName := []byte("agent_sessions")
	err = db.Update(func(tx *bolt.Tx) error {
		_, err := tx.CreateBucketIfNotExists(bucketName)
		return err
	})
	if err != nil {
		db.Close()
		return nil, err
	}

	return &BoltSessionStore{db: db, bucketName: bucketName}, nil
}
```

---

## 4. Verification & Testing Loops

*   **Status**: Integrated
*   **Target Configuration**: `/Users/tbmetin/repos/agents/.pre-commit-config.yaml`
*   **Action**: Created pre-commit config running static analysis and unit tests:

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: local
    hooks:
      - id: mypy-typecheck
        name: Static Type Check (mypy)
        entry: mypy --strict telegram-bridge/src/
        language: system
        types: [python]
        pass_filenames: false

      - id: python-unit-tests
        name: Run Python Unit Tests
        entry: pytest --cov=telegram-bridge/src --cov-fail-under=80 telegram-bridge/tests/
        language: system
        types: [python]
        pass_filenames: false
```
