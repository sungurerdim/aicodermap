@echo off
REM ds-tune evaluation harness for aicodermap (Windows native cmd.exe).
REM POSIX equivalent: auto/bench.sh — both call the same auto/eval.py.

cd /d "%~dp0\.."
python auto\eval.py > auto\run.log 2>&1
