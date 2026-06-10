@echo off
REM ds-tune evaluation harness for aicodermap (Windows native cmd.exe).
REM POSIX equivalent: ds/tune/bench.sh — both call the same ds/tune/eval.py.

cd /d "%~dp0\..\.."
python ds\tune\eval.py > ds\tune\run.log 2>&1
