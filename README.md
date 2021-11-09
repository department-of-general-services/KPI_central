# KPI_reference
Intended to facilitate sharing information about KPIs and how we compute them.
=======
This repository is intended to facilitate sharing information about the Facilities Management Division's key performance indicators (KPIs) and how they are computed.

Note that the notebooks in this repository draw their data from Archibus. And they draw that data not from the raw operational tables, but from the same SQL views that supply data to the Facilities Management Division's dashboard within Archibus. 

This means that many pre-processing stages have already taken place: 

- Consolidation of 100+ problem types into 30 primary problem types
- Insertion of a specific completion benchmark for each work request
- Computation of whether each work request was on time

To see the details of these steps, please view [the SQL file used to execute them here](https://github.com/department-of-general-services/fmd_archibus_dashboard/blob/master/create_views_facilities_dashboard.sql).

### Made With

- **Project Dependencies**
  - [SQLAlchemy](https://github.com/sqlalchemy/sqlalchemy) - A python toolkit and Object Relational Mapper (ORM) for managing connections to relational databases
  - [pandas](https://github.com/pandas-dev/pandas) - A python toolkit commonly used to manipulate and analyze tabular data
  - [seaborn](https://seaborn.pydata.org/) - A python toolkit and API for data visualization
  - [voila](https://pypi.org/project/voila/) A python toolkit for interactive data visualization
- **Development Dependencies**
  - [tox](https://tox.readthedocs.io/en/latest/) - Automates and standardizes the creation of testing environments.
  - [pytest](https://docs.pytest.org/en/6.2.x/) - Simplifies the design and execution of both unit and integration testing.
  - [black](https://black.readthedocs.io/en/stable/) - Autoformats code for consistent styling.
  - [flake8](https://flake8.pycqa.org/en/latest/) - Checks that code complies with PEP8 style guidelines.
  - [pre-commit](https://pre-commit.com/) - Runs code quality checks before code is committed.

### Project Structure

The list below represents a summary of important files and directories within the project.

  - `src/kpicentral/` The main python package for this project
  - `tests/` No tests yet but this is where they should go when implemented
  - `setup.py` Details about the package in `src/kpicentral/` and the file that facilitates installation of that package
  - `requirements.txt` The project's development dependencies
- `documents/` Contains documentation about the project
  - `notebooks/` Contains all relevant Jupyter notebooks with exploratory data analysis and visualization

## Getting Started

### Prerequisites

- Python installed on your local machine, preferably a version between 3.7 and 3.9

In order to check which version of python you have installed, run the following in your command line, and the output should look something like this:

> **NOTE**: in all of the code blocks below, lines preceded with $ indicate commands you should enter in your command line (excluding the $ itself), while lines preceded with > indicate the expected output from the previous command.

```
$ python --version
> Python 3.9.0
```

If you receive an error message, or the version of python you have installed is not between 3.7 and 3.9, consider using a tool like [pyenv](https://github.com/pyenv/pyenv) (on Mac/Linux) or [pyenv-win](https://github.com/pyenv-win/pyenv-win) (on Windows) to manage multiple python installations.

### Installation

1. [Clone the repository](https://docs.github.com/en/github/creating-cloning-and-archiving-repositories/cloning-a-repository-from-github/cloning-a-repository) on your local machine: `git clone https://github.com/department-of-general-services/priority-vendor-aging-report.git`
1. Create a new virtual environment: `python -m venv env`
1. Activate the virtual environment
   - On Mac/Linux: `source env/bin/activate`
   - On Windows: `.\env\Scripts\activate`
1. Install this package in editable mode by running `pip install -e .` which makes changes made to scripts within this package available without re-installing it.
1. Install the other dependencies required to contribute to the project: `pip -r requirements.txt`
1. Install `pre-commit` to autoformat your code: `pre-commit install`
1. Install the jupyter notebook extensions by running: `jupyter contrib nbextension install --user`
1. Create a new file named `.secrets.toml` and add the name of the server and database:
```
[DEVELOPMENT]
faster_web_server = "server_name"
faster_web_db = "database_name"
```
1. Run unit and integration tests by running `pytest`. Currently there are no tests, so you will see the line:

```
collected 0 items
```

