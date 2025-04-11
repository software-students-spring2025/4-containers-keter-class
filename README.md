![Lint-free](https://github.com/nyu-software-engineering/containerized-app-exercise/actions/workflows/lint.yml/badge.svg)
![web-app](https://github.com/software-students-spring2025/4-containers-keter-class/actions/workflows/web-app-build.yml/badge.svg?event=pull_request)
![ml-client](https://github.com/software-students-spring2025/4-containers-keter-class/actions/workflows/ml-client-build.yml/badge.svg?event=pull_request)


# Keter Class
This application is a web page that helps you track your credit cards. Uses computer vision to convert credit card to plain text and stores in mongodb, and is displayed on a dashboard. Users can take a photo of their credit card using their camera, and can access saved card information through the dashboard. Please use example credit cards in `machine-learning-client/Images` unless you want your bank account information potentially stolen.

# Team
* Brian Zou [Brian's Github](https://github.com/brianzou03)
* Bryant To
* Anna Ye [Anna's Github](https://github.com/AnnaTheYe)
* Andrew Bao

# How to Run via Docker
### Full Application
```
cd 4-containers-keter-class
pipenv shell
docker-compose up --build
```

### Machine Learning Client
```
cd machine-learning-client
pipenv shell
pip install -r requirements.txt
docker build -t credit-card-ocr .
docker run -p 5001:5001 -v ${PWD}/client_secrets.json:/app/client_secrets.json credit-card-ocr
```

# Running without Docker (Mac instructions)
## Web App
```
cd web-app
python3 -m venv venv
source venv/bin/activate 
pip install -r requirements.txt
brew tap mongodb/brew
brew uninstall mongodb-community
brew cleanup
brew install mongodb/brew/mongodb-community
brew services start mongodb/brew/mongodb-community
./venv/bin/python run.py
```

### Unit tests for web-app
```
cd web-app
pipenv run pytest --cov=app --cov-report=term-missing
```

## Machine Learning Client
```
cd machine-learning-client
python3 -m venv venv
source venv/bin/activate 
pip install -r requirements.txt
./venv/bin/python main.py

```


### Unit tests for machine learning client
```
cd machine-learning-client
pipenv run pytest --cov=main --cov-report=term-missing
```

# [Task Board Link](https://github.com/orgs/software-students-spring2025/projects/171)

# Technology
* Python / Flask
* Docker
* MongoDB
* CV Library (here)

