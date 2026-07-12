# Delegation Policy

## Decision Tree

```
Is the task mechanical and well-defined (renaming, refactoring, boilerplate, single-function impl)?
  Yes → delegate to `[delegation].subagent`, if granted in `[capabilities].subprocess`
  No  → handle inline

Does the task require multi-turn conversation history or session context?
  Yes → handle inline

Is the task description ambiguous?
  Yes → clarify BEFORE delegating — never delegate ambiguous tasks

Is the delegation target's remote provider unreachable, or is the code proprietary?
  Yes → fall back to the subagent's local/offline mode (no tools), if one is configured
  No local fallback configured → handle inline

Does the task involve security constraints (write-restricted repos, read-only sources)?
  Yes → handle inline so constraint enforcement can be verified directly
```

Example: a fully-granted host might set `[delegation].subagent = "pi-harness"` with a local `ollama/qwen2.5-coder:7b` fallback for offline/no-tool execution.

## How to Delegate

Invoke `[delegation].subagent` (from the manifest) if its command is present in
`[capabilities].subprocess`; otherwise handle the task inline. A typical subagent CLI exposes:

- a status/health check, run before delegating
- a default invocation that auto-selects a provider
- a forced-local/offline mode (no tool use)
- a flag to skip resource ceilings (debugging only — avoid in normal use)

Output is typically JSON with a `content` field. Apply file edits with the Edit tool.

Example: `pi-harness --status` checks health, `pi-harness "TASK"` auto-selects a provider, `pi-harness --model ollama/qwen2.5-coder:7b "TASK"` forces local (no tools), and `pi-harness --no-cgroup "TASK"` skips the memory ceiling (debugging only).

## Provider Routing

1. **Remote provider** (default — more capable; whichever the subagent is configured to use)
2. **Local fallback model** (used when the remote provider is unreachable; typically no tool use)

Example: OpenRouter free tier as the default remote provider, with local Ollama `qwen2.5-coder:7b` as the fallback.

## Rate Limit Handling

If delegation fails immediately (rate limit hit):
1. Run the subagent's status/health check to confirm the cause
2. Fall back to the subagent's local/offline mode for local execution
3. Or implement inline in this session

## Tasks Suitable for Delegation

- Renaming, refactoring, or boilerplate generation
- Mechanical test stub generation from a spec
- Structured data extraction from a specific file using a dedicated extraction tool
- Single-function implementation with a clear, unambiguous spec
- Bulk search or grep across many files

## Tasks That Must Stay Inline

- Architecture decisions or novel reasoning
- Multi-turn debugging sessions
- Ambiguous requirements (clarify first, then delegate if appropriate)
- Any task touching security constraints (POST/PATCH/DELETE to GitHub, etc.) — inline oversight required
- Verification of another subagent's output (verify inline, never chain subagents for verification)
- Tasks requiring the full conversation history to understand scope

## Stack Management

Check and repair the delegation subagent's own dependency stack (e.g. a local model
server) using whatever health-check and repair commands it exposes.

Example: `pi-harness --status` (health check), `pi-harness --repair` (restart Ollama if down), `sudo systemctl status ollama` (service status), `ollama list` (installed models).
