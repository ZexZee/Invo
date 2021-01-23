@echo off
@title Cleaning project files ...
cls
black main.py
black Lib/casino.py
black Lib/backend.py
black Lib/user.py
black Lib/item.py
black Lib/util.py