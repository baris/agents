# Actionable Agent Development Guidelines

This document serves as a developer-reference guide for building reliable AI agent harnesses. It translates key findings from 18 foundational resources into actionable design rules, architectural constraints, and metrics.

---

## 1. Execution & Control Flow

### 1.1 ReAct Loop
*   **Idea Source**: *ReAct: Synergizing Reasoning and Acting in Language Models* (Yao et al., 2022)
*   **Design Implications**:
    *   Interleave thoughts, actions, and observations sequentially.
    *   Enforce structured token stream parsing to pause generation immediately when tool-use patterns are identified (e.g., `Action: [tool_name]`).
    *   Inject tool results directly as an `Observation:` prefix.
*   **Metrics to Monitor**:
    *   **Success Rate**: Target ALFWorld task success (>90%) or QA accuracy.
    *   **Hallucination Rate**: Measure reasoning errors; aim to keep under 20% on multi-hop reasoning tasks.

### 1.2 Reflexion & Self-Correction
*   **Idea Source**: *Reflexion: Systematic Self-Reflection Task Feedback* (Shinn et al., 2023)
*   **Design Implications**:
    *   Maintain a stateful, multi-trial loop containing an execution actor, an automated evaluator (e.g., unit test runners), and an self-reflection writer.
    *   On failure, pass error output logs and stack traces to a self-reflection prompt.
    *   Store the resulting reflection in an episodic buffer and append it to the context of subsequent runs.
*   **Metrics to Monitor**:
    *   **Solve Rate vs. Trial Count**: Track how accuracy scales over 1–5 attempts (aim to improve coding benchmarks like HumanEval by >20% within 3 trials).
    *   **Reflection Quality**: Rate of recovery from syntax or logic failures on subsequent trials.

### 1.3 Cognitive Architectures (CoALA)
*   **Idea Source**: *Cognitive Architectures for Language Agents* (Sumers et al., 2023)
*   **Design Implications**:
    *   Decouple the controller agent from memory registers.
    *   Maintain distinct registers: Working Memory (active context), episodic history, semantic indexes, and procedural rules.
    *   Expose internal memory management (reading/writing) as distinct actions alongside external tools.
*   **Metrics to Monitor**:
    *   **Task Scalability**: Monitor context usage growth on long tasks (target sub-linear context usage scales).
    *   **Retrieval Recall**: Percentage of correct memory nodes retrieved for reasoning steps.

### 1.4 Loop Guards & Iteration Bounds
*   **Idea Source**: *Auto-GPT* (Significant Gravitas, 2023)
*   **Design Implications**:
    *   Enforce hard loop boundaries to prevent recursive loops.
    *   Compare command logs dynamically using semantic similarity (e.g., cosine distance of command logs) to detect repetitive actions.
    *   Trigger Human-in-the-Loop (HITL) authorization gates for high-risk actions.
*   **Metrics to Monitor**:
    *   **Runaway Loop Rate**: Target 0% infinite loops in execution logs.
    *   **Cost-per-Task**: Financial budget caps per session.

### 1.5 Multi-Agent Orchestration
*   **Idea Source**: *AutoGen* (Wu et al., 2023)
*   **Design Implications**:
    *   Structure workflows as message exchanges between specialized agents with narrow system prompts.
    *   Define concrete communication channels and type-safe schemas for agent-to-agent (A2A) handoffs.
*   **Metrics to Monitor**:
    *   **Inter-agent Communication Overhead**: Minimize token overhead; target <30% of total tokens spent on routing.
    *   **Review Efficiency**: Reduction in bug counts after collaborative validation runs.

### 1.6 Statecharts & Checkpointing
*   **Idea Source**: *LangGraph* (LangChain, 2024)
*   **Design Implications**:
    *   Define loop structures as directed graphs with typed state variables.
    *   Perform atomic state writes to a transactional database at node boundaries.
    *   Allow manual time-travel debugging by keeping state histories version-controlled.
*   **Metrics to Monitor**:
    *   **State Conflict Rate**: Target 0% database commit conflicts or unmapped state transitions.
    *   **Recovery Time**: Latency to reload state and resume execution after a crash (target <100ms).

---

## 2. Context & Memory Management

### 2.1 Virtual Memory Paging
*   **Idea Source**: *MemGPT: Towards LLMs as Operating Systems* (Packer et al., 2023)
*   **Design Implications**:
    *   Maintain a compact "main memory" containing static rules and a sliding message queue.
    *   Offload long documents and old dialogue turns to database-backed "archival memory" or semantic search vectors.
    *   Provide tools for the agent to explicitly retrieve, index, and page memory nodes.
*   **Metrics to Monitor**:
    *   **Deep Recall Rate**: Retrieval accuracy on facts buried in long histories (>95%).
    *   **Active Context Footprint**: Keep average context usage under 30% of the model's total window limit.

### 2.2 Spatial Prompt Optimization
*   **Idea Source**: *Lost in the Middle: How Language Models Use Long Contexts* (Liu et al., 2023)
*   **Design Implications**:
    *   Sort prompt segments by relevance profiles.
    *   Place high-importance system rules, core constraints, and system prompts at the beginning (top).
    *   Place the active conversation state, execution commands, and user responses at the end (bottom).
    *   Place reference document chunks and tool feedback histories in the middle.
*   **Metrics to Monitor**:
    *   **Lost-in-Middle Retrieval Accuracy**: Evaluate recall of facts located in the middle of a 20k token prompt (target >80% accuracy).

### 2.3 Prompt Compression
*   **Idea Source**: *LLMLingua* (Jiang et al., 2023)
*   **Design Implications**:
    *   Filter bulky outputs (e.g., execution logs or raw web pages) using a local compression model before sending them to the primary LLM context window.
    *   Prune low-information-density (low perplexity) tokens from prompt payloads.
*   **Metrics to Monitor**:
    *   **Compression Ratio**: Target 5x to 20x compression of raw documents.
    *   **Accuracy Preservation**: Reasoning score delta on compressed prompts (target <5% loss).

### 2.4 Episodic Memory Consolidation
*   **Idea Source**: *Generative Agents* (Park et al., 2023)
*   **Design Implications**:
    *   Run asynchronous background jobs to summarize low-level logs into high-level concept observations.
    *   Index consolidated concepts semantically to serve as associative planning nodes in subsequent runs.
*   **Metrics to Monitor**:
    *   **Memory Freshness & Decay**: Measure semantic drift of long-term memories over time.
    *   **Behavioral Consistency**: Target stable task execution behavior under changing user contexts.

---

## 3. Tool & API Interface Design

### 3.1 Inline API Embedding
*   **Idea Source**: *Toolformer* (Schick et al., 2023)
*   **Design Implications**:
    *   Optimize tools for direct string parsing and inline evaluation during LLM text generation.
    *   Enforce strict parsing regex boundaries for inline tool syntaxes.
*   **Metrics to Monitor**:
    *   **Invocation Accuracy**: Match rates between intended API calls and executed tags.
    *   **Tool Calling Latency**: Target <50ms parsing overhead to intercept the token stream.

### 3.2 Dynamic Tool Retrieval
*   **Idea Source**: *Gorilla* (Patil et al., 2023)
*   **Design Implications**:
    *   Maintain tool definitions in a semantic vector registry.
    *   Based on user intent, retrieve only the top-N (N < 10) most relevant tool schemas and inject them dynamically into the context.
    *   Avoid dumping the entire toolset into the system prompt.
*   **Metrics to Monitor**:
    *   **Schema Hallucination Rate**: Keep tool-call syntax violations at 0%.
    *   **Registry Retrieval Accuracy**: Target >98% success in retrieving the correct tool schema for a user query.

### 3.3 Protocol Standardization (MCP)
*   **Idea Source**: *Model Context Protocol Specification* (Anthropic, 2024)
*   **Design Implications**:
    *   Use JSON-RPC 2.0 over standard I/O pipes or SSE for all tool integration.
    *   Separate the client harness from external server tools.
    *   Expose inputs as resources and commands as tools.
*   **Metrics to Monitor**:
    *   **Integration Time**: Minimize time to add new tools.
    *   **Transport overhead**: Maintain <5ms latency on RPC requests.

### 3.4 Code-as-a-Skill Execution
*   **Idea Source**: *Voyager* (Wang et al., 2023)
*   **Design Implications**:
    *   Let the agent write scripts to solve complex multi-step workflows.
    *   Validate written scripts in a sandbox environment and save successful scripts as reusable tools.
    *   Expose the script library via semantic index lookup.
*   **Metrics to Monitor**:
    *   **Code Compilation Success Rate**: Target >90% compilation rates for agent-written tools.
    *   **Reusability Index**: Measure how frequently synthesized skills are reused on subsequent tasks.

### 3.5 Parallel Task Execution
*   **Idea Source**: *LLM Compiler* (Kim et al., 2023)
*   **Design Implications**:
    *   Decompose non-dependent operations into parallel execution trees (DAGs).
    *   Execute tool threads concurrently using async programming blocks before returning the unified observation block to the LLM.
*   **Metrics to Monitor**:
    *   **Wall-Clock Speedup**: Target >3x faster execution compared to sequential ReAct.
    *   **Token Savings**: Reduction in duplicate reasoning prompt tokens.

---

## 4. Sandbox Security & Verification

### 4.1 Test-Driven Verification
*   **Idea Source**: *SWE-bench* (Jimenez et al., 2023)
*   **Design Implications**:
    *   Force agents to produce localized diff patches instead of full-file overwrites.
    *   Expose unit-test execution as a required step before changes are validated.
    *   Feed test results, compilers, and linter errors directly back into the self-reflection loop.
*   **Metrics to Monitor**:
    *   **Resolve Rate**: Percentage of task issues successfully patched and verified.
    *   **Cleanliness Score**: Target 0% regression on unmodified code lines.

### 4.2 API Abstraction
*   **Idea Source**: *AgentBench* (Liu et al., 2023)
*   **Design Implications**:
    *   Wrap low-level, high-risk interfaces (databases, network configuration, shell utilities) in structured, validated wrapper APIs.
    *   Validate all query syntaxes before dispatching commands.
*   **Metrics to Monitor**:
    *   **Syntax Error Rate**: Keep invalid commands or queries under 5%.

### 4.3 Containerized MicroVM Sandbox
*   **Idea Source**: *gVisor / WebAssembly / Docker Sandboxing*
*   **Design Implications**:
    *   Execute all commands and scripts inside a restricted container runtime (e.g., Docker running on gVisor).
    *   Enforce read-only systems with small writable scratch spaces.
    *   Configure strict timeouts (e.g., 30s) and memory caps (e.g., 128MB) at the runtime level.
    *   Block sandbox outbound network access unless explicitly authorized.
*   **Metrics to Monitor**:
    *   **Sandbox Startup Latency**: Target <150ms for MicroVMs or <1ms for WASM.
    *   **Escape Prevention Rate**: Enforce 100% block rates on filesystem breakouts and host network calls.
