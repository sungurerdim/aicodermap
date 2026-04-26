#!/bin/bash
# ds-tune evaluation harness for aicodermap.
# Runs auto/eval.py against current data/sources-whitelist.json + auto/fixtures.json.
# Output: auto/run.log (grep-able for hit_rate_at_1 / hit_rate_at_3).

set -e
cd "$(dirname "$0")/.."
python auto/eval.py > auto/run.log 2>&1
