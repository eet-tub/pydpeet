# Installation


:::{card} If you already have a Python environment set up, you can {ref}`skip directly to the PyDPEET installation <install-pydpeet>`.
:::


```{note}
PyDPEET requires Python 3.12 or newer.
```

You can use the editor or IDE of your choice. We recommend VS Code, but PyDPEET also works with other editors, notebooks, and Python environments.

You can install and use PyDPEET with different Python environment tools, such as `uv`, `Python/pip`, or `conda`. We recommend uv, because it is fast, simple to use, and provides reproducible project environments.

## 1. Install Python or an environment manager

::::{tab-set}

:::{tab-item} uv
:sync: uv

Install `uv` by following the official installation instructions:

```text
https://docs.astral.sh/uv/getting-started/installation/
```

`uv` can automatically install and manage Python versions for your project.

:::

:::{tab-item} Python/pip
:sync: pip

Install Python 3.12 or newer from:

```text
https://www.python.org/downloads/
```
:::

:::{tab-item} conda
:sync: conda

Install Miniconda from:

```text
https://docs.anaconda.com/miniconda/
```
:::

::::

## 2. Open or create a project folder
::::{card}
:class-card: sd-border-secondary
Choose or create a folder in which you want to use PyDPEET and open a terminal in this folder.

You can use either a system terminal or the integrated terminal of your editor or IDE (for example VS Code).
::::
## 3. Create an environment

::::{tab-set}

:::{tab-item} uv
:sync: uv

Create a new uv project with Python 3.12:

```bash
uv init
uv python pin 3.12
```

:::

:::{tab-item} Python/pip
:sync: pip

Create a local virtual environment:

```bash
python -m venv .venv
```

Activate the environment.

### Windows

```powershell
.venv\Scripts\activate
```

### Linux/macOS

```bash
source .venv/bin/activate
```

:::

:::{tab-item} conda
:sync: conda

Create a dedicated conda environment:

```bash
conda create -n pydpeet python=3.12
```

Activate it:

```bash
conda activate pydpeet
```

:::

::::

(install-pydpeet)=
## 4. Install PyDPEET

::::{tab-set}

:::{tab-item} uv
:sync: uv

Add PyDPEET to your uv project:

```bash
uv add pydpeet
```

:::

:::{tab-item} Python/pip
:sync: pip

Install PyDPEET with pip:

```bash
python -m pip install --upgrade pip
python -m pip install pydpeet
```

:::

:::{tab-item} conda
:sync: conda

Install PyDPEET from PyPI inside your conda environment:

```bash
python -m pip install --upgrade pip
python -m pip install pydpeet
```

```{note}
PyDPEET is currently distributed via PyPI. Therefore, even when using `conda`, PyDPEET itself is installed with `pip`.
```

:::

::::

## 5. Update PyDPEET
```{note}
PyDPEET is actively developed. We recommend updating regularly.
```


::::{tab-set}

:::{tab-item} uv
:sync: uv

```bash
uv add --upgrade pydpeet
```

:::

:::{tab-item} Python/pip
:sync: pip

```bash
python -m pip install --upgrade pydpeet
```

:::

:::{tab-item} conda
:sync: conda

```bash
python -m pip install --upgrade pydpeet
```
:::
::::

## Next steps

We recommend starting with the [examples](examples/index.md).