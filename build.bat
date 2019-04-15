@echo off
rd /s /q .\dist
python setup.py bdist_wheel --universal