# Tool setup and run
To run correctly, the script requires proper setup according to the instructions below. It can be executed on any windows or linux machine.

Download the latest stable version of the code as zip from [**here**](https://github.com/GFDRR/CCDR-tools/tree/main/tools/code). Unzip it in your work directory, e.g. wd/RDL-tools/.
The script has been developed to run as [jupyter notebook](https://jupyter.org/), but also allows to run as pure python (`manual_run.py`). 

## Python environment
- Python 3 needs to be installed on your system. We suggest the latest [Anaconda](https://www.anaconda.com/download) distribution. Mamba is also encouraged.
- Create new `RDL-tools` environment from the provided rdl-tools.yml file. It can be done via Anaconda navigator interface (environments > Import ) or from the Anaconda cmd prompt:
  ```bash
  conda create --name RDL-tools --file <dir/rdl-tools.yml>`
  activate RDL-tools
  ```

## Settings
Edit the `.env` file inside the notebook directories to specify your working directory:

```
# Environment variables for the CCDR Climate and Disasater Risk analysis notebooks

# Fill the below with the location of data files
# Use absolute paths with forward slashes ("/"), and keep the trailing slash
DATA_DIR = C:/Workdir/RDL-tools
```

## Run Jupyter notebooks
- Navigate to your working directory: `cd <Your work directory>`
  ```bash
  cd C:/Workdir/RDL-tools
  ```
- Run the jupyter notebook.
  ```bash
  jupyter notebook GUI.ipynb
  ```
The main interface should pop up in your browser.

```{figure} images/GUI.png
---
width: 100%
align: center
---
```
Select the hazard of interest to open the analytical notebook. E.g. for floods:

```{figure} images/GUI_F3.png
---
width: 100%
align: center
---
```