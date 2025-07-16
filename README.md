# python_project_template

[![Github Actions Workflow](https://github.com/DiogoCarapito/python_project_template/actions/workflows/main.yaml/badge.svg)](https://github.com/DiogoCarapito/python_project_template/actions/workflows/main.yaml)

Personal python project template

Python version: 3.12

## cheat sheet

### setup

move all files and folders to the current project folder

```bash
mv python_project_template/{*,.*} . && rm -r python_project_template/
```

### venv

create venv

```bash
python3.12 -m venv .venv
```

activate venv

```bash
source .venv/bin/activate
```

### Docker

build docker image

```bash
docker build -t main:latest .
```
