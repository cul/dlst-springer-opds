# CUL Springer OPDS Feed

Creates an OPDS 2.0 feed from the Springer API.

## Dependencies

* Python 3 (tested on 3.9)
* [SQLAlchemy 1.4](https://docs.sqlalchemy.org/en/14/)
* [requests](https://pypi.org/project/requests/)


## Configuring

Configurations are stored in `local_settings.cfg`. This file is excluded from version control, and you will need to create this file with values for your local instance. You can copy `local_settings.cfg.example` to `local_settings.cfg` and update it with your own values.


## Usage

To add Springer books loaded in the API since a certain amount of days ago, and create an OPDS 2.0 feed from that data, run:

```
update_feed.py <number of days>
````


## Contributing

### Style

This project uses the Python PEP8 community style guidelines. To conform to these guidelines, the following linters are part of the pre-commit:

* black formats the code automatically
* flake8 checks for style problems as well as errors and complexity
* isort sorts imports alphabetically, and automatically separated into sections and by type

After locally installing pre-commit, install the git-hook scripts in the project's directory:

    pre-commit install

### Documentation

Docstrings should explain what a module, class, or function does by explaining its syntax and the semantics of its components. They focus on specific elements of the code, and less on how the code works. The point of docstrings is to provide information about the code you have written; what it does, any exceptions it raises, what it returns, relevant details about the parameters, and any assumptions which might not be obvious. Docstrings should describe a small segment of code and not the way the code is implemented in a larger environment.

This project adheres to [Google’s docstring style guide](https://google.github.io/styleguide/pyguide.html#381-docstrings). There are two types of docstrings: one-liners and multi-line docstrings. A one-line docstring may be perfectly appropriate for obvious cases where the code is immediately self-explanatory. Use multiline docstrings for all other cases.

### Tests

New code should have unit tests. Tests are written in [unittest style](https://docs.python.org/3/library/unittest.html) and run using [tox](https://tox.readthedocs.io/).

