![Python](https://img.shields.io/github/pipenv/locked/python-version/kwzrd/aitchi?label=Python&style=flat-square)
![Flake8 & friends](https://img.shields.io/github/workflow/status/kwzrd/aitchi/Checks?label=Flake8%20%26%20friends&style=flat-square)

# Aitchi

Discord bot for the XCX community, notifying of new TikTok activity.

This is a private bot intended for a single community. It is not possible to invite it to your own guild. However, you are welcome to fork the repository and host your own instance, or simply use the code for reference when developing your own solution.

## Installation

First, make a copy of the [`.env.template`](.env.template) file named `.env`, and fill in the required secrets for your instance.

To configure, you can either change the [`production.json`](aitchi/config/environments/production.json) file, or make a copy called `development.json` in the same directory. This file will be automatically ignored by version control, and the bot will use it over the production one.

We use [Pipenv](https://pypi.org/project/pipenv/) for dependency management. Recreate the environment:

```
pipenv sync
```

Run the project:

```
pipenv run aitchi
```

## Contributing

If you are interested in contributing, please get in touch with me first.
