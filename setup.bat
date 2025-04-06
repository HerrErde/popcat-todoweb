@echo off

echo Setting up...
python -m venv .venv
call .venv\Scripts\activate

cd src

echo Installing packages...
echo Upgrade Pip...
python.exe -m pip install --upgrade pip > nul
pip install -r requirements.txt

echo Finished...

exit