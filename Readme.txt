install a new venv
python3 -m venv .venv

activate virtual environmen 
source env/bin/activate

in case you have a virtualenvironment please run this, where [VENV_NAME] is the name of the virtual environment.
python3 -m ipykernel install --user --name=[VENV_NAME]
or 
ipython kernel install --user --name=[VENV_NAME]

pip3 install -r requirements.txt