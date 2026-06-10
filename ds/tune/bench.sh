#!/bin/bash
# ds-tune evaluation harness for aicodermap.
# Runs ds/tune/eval.py against current data/sources-whitelist.json + ds/tune/fixtures.json.
# Output: ds/tune/run.log (grep-able for hit_rate_at_1 / hit_rate_at_3).

set -e
cd "$(dirname "$0")/../.."
python ds/tune/eval.py > ds/tune/run.log 2>&1
