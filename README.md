![Lint-free](https://github.com/nyu-software-engineering/containerized-app-exercise/actions/workflows/lint.yml/badge.svg)

# Keter Class
Our application contains the following: web page that helps you track your credit cards. Uses computer vision to convert credit card to plain text and stores in mongodb, and is displayed.

# Team
* Brian Zou [Brian's Github](https://github.com/brianzou03)
* Bryant To
* Anna Ye
* Andrew Bao

# How to Run via Docker
```

```

### Running without Docker (Mac instructions)
```
cd web_app
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

# Unit tests for web_app
```
cd web_app
pytest
```

# Unit tests for machine learning client
```
cd machine-learning-client
pytest
```


# Technology
* Python / Flask
* Docker
* MongoDB
* CV Library (here)

