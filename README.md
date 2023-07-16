# Model deployment project

Please do not fork this repository, but use this repository as a template for your refactoring project. Make Pull Requests to your own repository even if you work alone and mark the checkboxes with an x, if you are done with a topic in the pull request message.

## Project for today
The task for today you can find in the [project-description.md](project-description.md) file.

## Answer these questions

1. What is the RMSE of your model?
    rmse:  4.4331545356692965
2. What would you do differently if you had more time?
    I would practice the testing methods I saw this week in the bootcamp and test my data and my model.

## Project files
1. [ML Model](src/model.py) | [ML model notbook](02-train-ml-model.ipynb) | [ML model refacturing notebook](test.ipynb)
2. [Model_gesitrations](03_register_mlflow_model.ipynb)
3. [Webservice_locally](webservice_locally)
4. [Webservice_deployment](webservice_deployment)


## Environment

You need the google cloud sdk installed and configured. If you don't have it installed follow the instructions [here](https://cloud.google.com/sdk/docs/install) or use homebrew on mac:

```bash
brew install --cask google-cloud-sdk
```

Python environment:

```bash
pyenv local 3.11.3
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

## IMPORTANT

Don't forget to **STOP** the `Cloud Services` after you are done, especially the `SQL Instance`. You can always start them again when you need them.