#!/bin/bash
# launch_tmux.sh - Launch tmux panes for parallel agent development

SESSION="dana-dev"

# Create session
tmux new-session -d -s "$SESSION"

# Split into 4 panes
tmux split-window -h
tmux split-window -v
tmux select-pane -t 0
tmux split-window -v

# Setup panes
tmux send-keys -t 0 "cd ~/projects/my-agent && claude" C-m
tmux send-keys -t 1 "cd ~/projects/my-agent && gemini" C-m
tmux send-keys -t 2 "cd ~/projects/my-agent && opencode" C-m
tmux send-keys -t 3 "cd ~/projects/my-agent && grok" C-m

# Attach
tmux attach-session -t "$SESSION"
