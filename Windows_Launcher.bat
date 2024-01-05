@echo off
color A
pip install --upgrade pip
pip install -r requirements.txt
cls
start /B python gui.py