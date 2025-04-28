@echo off

REM Step 1: Create a virtual environment using Python 3.12
py -3.12 -m venv .venv

REM Step 2: Activate the virtual environment
call .venv\Scripts\activate.bat

REM Step 3: Upgrade pip
python -m pip install --upgrade pip

REM Step 4: Install dependencies
pip install -r requirements.txt

REM Step 5: Install pillow
python -m pip install Pillow

