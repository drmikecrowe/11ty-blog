#!/usr/bin/env bash
#
# Watching backlog — fill in the --rank value (1=top .. 5=good) for each entry,
# then run this script. Drop the --rank flag entirely for anything you don't
# want to rank. Each line prompts you to pick the right IMDB match.
#
#   Run all:        ./scripts/watching-todo.sh
#   Run one:        copy/paste a single line below
#
# Flags you may want to add per entry:
#   --highly-recommended   (a.k.a. --highly)   top picks
#   --currently-watching                       still in progress
#   --no-draft                                 publish immediately (default: draft)
#   --entries 1                                skip the match prompt (auto-pick first)
#
set -euo pipefail
cd "$(dirname "$0")/.."

run() { mise exec -- uv run python scripts/create-watching-post.py "$@"; }

# ── TV Shows ────────────────────────────────────────────────────────────────
# run "Widow's Bay"            --tv --date 2026-06-17 --rank 4
