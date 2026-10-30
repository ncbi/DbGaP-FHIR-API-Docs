# Notebook examples

This folder contains the
[dbGaP and SRA download demo](download_all_dbGaP_phenotype_dataset_demo.ipynb) and its setup helper.

## Directory structure

- `*.ipynb` — notebooks. Each notebook describes its purpose and workflow inside the notebook.
- `helpers/` — Python helper modules imported by the notebooks. Keep this folder alongside the
  notebooks.
- requirements.txt — the file listing Python dependencies for the notebook.
- `tests/` — standalone tests for the notebook cells and setup helper.
- Downloaded files and other generated output may be created when you run a notebook.

## Running a notebook

Run these commands in a terminal from this folder. Python 3.10 or newer must be installed.

Create and activate a virtual environment:

```bash
python -m venv .venv
```

On macOS or Linux:

```bash
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install the notebook requirements, then launch Jupyter:

```bash
python -m pip install -r requirements.txt
python -m notebook
```

Jupyter opens in your browser. Select the notebook file and run its cells from top to bottom. Follow
any prompts; press Enter to accept a displayed default.

Downloaded files are saved to the output location shown by the notebook.

## Running the tests

From this folder, with Python 3.10 or newer and your virtual environment activated:

```bash
python -m pip install -r tests/requirements.txt
python -m pytest -c pytest.ini
```

The tests need only pytest and requests. They execute the notebook's actual code cells by their
human-readable IDs, mock download requests, and use temporary files and fake passports. They also
check that the notebook contains no saved outputs, execution counts, or cell metadata. Clear those
artifacts before committing a notebook that you have run.

Copy this entire folder to the documentation repository to keep the notebook, helper, and tests
together. The tests resolve the notebook and helper relative to this folder and do not import DRS
code or its pytest plugin. The DRS repository's `./test.sh` also collects these tests.
