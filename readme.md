# virtual env (Ubuntu)

`Install pip:`

    sudo apt-get install python3-pip

`Install virtual env:`

    sudo pip3 install virtualenv

    sudo apt install python3.8-venv

`Create vitrual env named sls-flask-env:`

    python3 -m venv sls-flask-env

`Activate virtual env:`

    source sls-flask-env/bin/activate

# Dependencies

`Make list of required dependencies:`

    pip freeze > requirements.txt

`Install from requirements.txt:`

    pip install -r requirements.txt