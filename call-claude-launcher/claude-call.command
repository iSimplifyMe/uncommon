#!/bin/zsh
# The session this launcher opens. Terminal runs this file in a new window.
export PATH="$HOME/.local/bin:/opt/homebrew/bin:$PATH"
cd "$HOME"
: "${CLAUDE_FLAGS:=--model claude-opus-5-5}"   # put your usual flags here or export CLAUDE_FLAGS
exec caffeinate -i claude ${=CLAUDE_FLAGS}
