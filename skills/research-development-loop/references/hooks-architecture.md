# Hook Architecture Reference

## Hook-to-Phase Mapping

Claude Code has 30 hook event types. The ones relevant to the RDL loop:

| Hook | Phase | Role |
|------|-------|------|
| `UserPromptSubmit` | Pre-Phase 0 | Primary enforcement gate — synchronous, blocking; runs before Claude processes the prompt. Used to dispatch the coding subagent (`[delegation].subagent`) on every user turn. |
| `PostToolUse(Skill)` | All phases | Drives state machine transitions — tracks which skill was invoked and asserts the correct phase sequence. |
| `Stop` | Phase 6 / goal gates | Fires when Claude stops; used for heartbeat writes and goal condition checks. |
| `PostToolUseFailure` | Phase 3/4 | Subprocess anomaly trigger — OOM exit (code 137), tool error, broken pipe. A subprocess OOM exits 137 → PostToolUseFailure fires → systematic debugging triggered. |
| `PermissionDenied` | Phase 3 | Environmental constraint anomaly — write attempt blocked by policy; triggers systematic debugging, not a retry. |
| `StopFailure` | Loop integrity | Loop failed to terminate cleanly; signals a missing back-edge or an unhandled Phase 3/4 anomaly. |
| `SessionStart` | Crash detection | Fires at the start of every session — used to detect unsurvivable crashes (see watchdog pattern below). |
| `SessionEnd` | Continuity | Fires when the session closes gracefully; writes clean_exit marker for the watchdog. May NOT fire on SIGKILL. |
| `PreCompact` | Research continuity | Fires before context compaction; opportunity to snapshot the current residual so Phase 0 state survives the window boundary. |

### Hooks that do NOT correspond to RDL phases

`PreToolUse`, `PostToolUse(Bash)`, `PostToolUse(Write)`, `PostToolUse(Read)`, `PostToolUse(Edit)`, `Notification`, `PostCompact` — useful for general development discipline (formatting, logging, latency monitoring) but not phase-specific RDL signals.

---

## Watchdog Pattern (Crash Detection)

Unsurvivable crashes (SIGKILL, parent OOM kill) do not fire SessionEnd — nothing fires. The only detection point is the NEXT SessionStart.

**Pattern:**

- `Stop` hook writes `.rdl-state/heartbeat` with current phase and timestamp
- `PostToolUse(Bash)` writes `.rdl-state/last-command` after heavy compute operations
- `SessionEnd` writes `.rdl-state/clean_exit` if the session terminated gracefully
- `SessionStart` reads `.rdl-state/`: if `heartbeat` exists but `clean_exit` is absent, the previous session was killed. If the killed session was in Phase 3 or 4, this is a Phase 3/4 anomaly — invoke systematic debugging

**Subprocess OOM (survivable) vs. parent OOM (unsurvivable):**

| Scenario | What fires | Detection |
|----------|------------|-----------|
| Subprocess exits 137 (OOM) | `PostToolUseFailure` | Fires immediately; systematic debugging triggered |
| Parent process SIGKILL | Nothing | Only detectable at next `SessionStart` via absence of `clean_exit` |

The parent OOM is the canonical example of a **survivable-bias blind spot**: the process that would record the failure is the one that was killed. No hook can fire from inside a dead process.

---

## The Survival Bias Problem

Every hook fires on something that happened — a tool that ran, a session that closed, a permission that was checked. Hooks are structurally blind to absences.

**What hooks cannot detect:**
- Tests that were never written (no `PostToolUse(Write)` for a test file → no test)
- Capabilities that were claimed but never demonstrated (no run → no output → no evidence)
- Failure modes that kill the process before any hook fires
- Tools that were never invoked (every un-invoked skill is invisible to the hook system)

**Implication for the RDL:** Passing all phase hooks does not mean the loop was complete — it means every phase that ran completed. Phases that didn't run fire no hooks. This is the structural motivation for:
1. The **N category** in the residual (in-model absence tracking, not event-driven)
2. The **mandatory negative inventory** in Phase 5 (explicit enumeration of what was NOT done)
3. The **Reject(P) analysis** in Step 0.7 (surfaces absence hypotheses before they become invisible failures)

The N category and negative inventory are the in-model remedies for the hook system's structural survival bias.
