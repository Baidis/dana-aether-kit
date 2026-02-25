#!/bin/bash
# launch_tmux.sh — Launch a tmux session with one pane per agent role.
#
# Usage (standalone):
#   ./scripts/launch_tmux.sh [session-name]
#
# Usage (driven by `aether coordinate --launch`):
#   ROLES_JSON=.aether/roles.json ./scripts/launch_tmux.sh
#
# Environment variables:
#   ROLES_JSON   — path to roles.json (default: .aether/roles.json)
#   PROJECT_DIR  — directory to cd into in each pane (default: current dir)

set -euo pipefail

SESSION="${1:-dana-dev}"
ROLES_JSON="${ROLES_JSON:-.aether/roles.json}"
PROJECT_DIR="${PROJECT_DIR:-$(pwd)}"

# ── Helpers ──────────────────────────────────────────────────────────────────

has_cmd() { command -v "$1" &>/dev/null; }

warn() { echo "⚠  $*" >&2; }

# ── Roles ────────────────────────────────────────────────────────────────────

if ! has_cmd jq; then
    warn "jq not found — falling back to hardcoded roles (claude / gemini / opencode / grok)"
    ROLES=("claude" "gemini" "opencode" "grok")
    ROLE_NAMES=("analyst" "researcher" "integrator" "critic")
else
    # Parse roles.json — extract names and cli values (skip coordinator / null CLIs)
    ROLE_NAMES=()
    ROLES=()
    while IFS=$'\t' read -r name cli; do
        [[ "$name" == "coordinator" ]] && continue
        [[ "$cli" == "null" ]] && continue
        ROLE_NAMES+=("$name")
        ROLES+=("$cli")
    done < <(jq -r 'to_entries[] | select(.value.cli != null) | [.key, .value.cli] | @tsv' "$ROLES_JSON" 2>/dev/null || true)
fi

if [[ ${#ROLES[@]} -eq 0 ]]; then
    warn "No roles with CLIs found — nothing to launch."
    exit 1
fi

# ── Session ──────────────────────────────────────────────────────────────────

# Kill existing session if present
tmux kill-session -t "$SESSION" 2>/dev/null || true

tmux new-session -d -s "$SESSION" -n "${ROLE_NAMES[0]}"

for i in "${!ROLES[@]}"; do
    role="${ROLE_NAMES[$i]}"
    cli="${ROLES[$i]}"

    if [[ $i -eq 0 ]]; then
        target="$SESSION:$role"
        tmux rename-window -t "$SESSION:0" "$role"
    else
        tmux new-window -t "$SESSION" -n "$role"
        target="$SESSION:$role"
    fi

    tmux send-keys -t "$target" "cd '$PROJECT_DIR'" Enter

    if has_cmd "$cli"; then
        tmux send-keys -t "$target" "$cli" Enter
    else
        warn "CLI '$cli' not found for role '$role' — pane opened but idle"
    fi
done

# Coordinator pane
tmux new-window -t "$SESSION" -n "coordinator"
tmux send-keys -t "$SESSION:coordinator" "cd '$PROJECT_DIR'" Enter

echo "✓ Session '$SESSION' launched with ${#ROLES[@]} role pane(s) + coordinator"
echo "  Attach with: tmux attach-session -t $SESSION"
tmux attach-session -t "$SESSION"
