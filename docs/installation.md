# Installation

PyDPEET is currently only distributed via PyPI. That means you install the package with `pip`, regardless of whether you manage your environment with a local `.venv` or with `conda`.

We recommend using a `conda` environment for PyDPEET, especially for beginners, because it makes it easier to manage Python versions cleanly and reduces setup friction when scientific dependencies are involved.

## Before you install PyDPEET

PyDPEET currently requires Python 3.12 or newer.

Choose one of the two setup paths below:

- Use the `conda` workflow if you are new to Python, want a cleaner scientific setup, or prefer environment management that includes the Python interpreter itself.
- Use the `.venv` workflow if you already have a suitable Python installation and want the standard Python environment workflow.

## Option 1: Installation with `conda`

### 1. Install Miniconda

1. Download and install Miniconda from the official [Miniconda website](https://www.anaconda.com/download/success?reg=skipped).
2. Open the Miniconda Prompt after installation.
3. Verify that `conda` is available:

```bash
conda --version
```

### 2. Create and activate a dedicated environment

```bash
conda create -n pydpeet python=3.12
conda activate pydpeet
```

### 3. Install PyDPEET from PyPI

Even in a `conda` environment, the package itself is currently installed from PyPI:

```bash
python -m pip install --upgrade pip
python -m pip install pydpeet
```

### 4. Keep the package up to date

Because the project is still evolving quickly, update the package regularly:

```bash
python -m pip install --upgrade pydpeet
```


## Option 2: Installation with `.venv`

### 1. Install Python

1. Download and install Python 3.12 or newer from the official Python website.
2. During installation on Windows, enable the option to add Python to your `PATH` if it is offered.
3. Open a new terminal and verify the installation:

```bash
python --version
```

### 2. Create a project environment

Open a terminal in your project folder and create a virtual environment:

```bash
python -m venv .venv
```

Activate it:

```bash
.venv\Scripts\activate
```

### 3. Install PyDPEET from PyPI

```bash
python -m pip install --upgrade pip
python -m pip install pydpeet
```

### 4. Keep the package up to date

PyDPEET is actively developed. New fixes, updates, and features are added very frequently, roughly every two weeks, so regular updates are recommended.

```bash
python -m pip install --upgrade pydpeet
```


## Working with PyDPEET in VS Code

After installation, you can open your folder in VS Code and select the interpreter that belongs to your environment:

- For `conda`, select the `pydpeet` environment interpreter.
- For `.venv`, select the interpreter inside `.venv`.


Once the correct interpreter is selected, you can run notebooks, scripts, and PyDPEET examples directly in VS Code. We recommend to start with our [examples](examples/index.md)
