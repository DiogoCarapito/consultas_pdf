# consultas_pdf

[![Github Actions Workflow](https://github.com/DiogoCarapito/python_project_template/actions/workflows/main.yaml/badge.svg)](https://github.com/DiogoCarapito/python_project_template/actions/workflows/main.yaml)

conversor de .pdf para .csv e .xlsx em PyQt6

Python version: 3.12

## como usar
### criar um ambiente virtual (venv)

criar venv

```bash
python3.12 -m venv .venv
```

activatar o ambiente virtual

```bash
source .venv/bin/activate
```

### instalar as dependências

```bash
make install
```

### executar o programa

```bash
python main.py <pasta ou ficheiro>
```

sendo que a pasta ou ficheiro é o caminho para o ficheiro ou pasta que se pretende processar com os ficheiros .pdf para converter.

irão ser criados os ficheiros .csv e .xlsx na pasta *processed*