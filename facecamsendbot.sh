#!/usr/bin/env sh
cd "$(dirname "$0")" || exit 1
if [ ! -f "./venv/bin/activate" ]; then
	python3 -m venv venv
	. "./venv/bin/activate"
	pip install -r requirements.txt
else
	. "./venv/bin/activate"
fi
python ./facecamsendbot.py "$@"
