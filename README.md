from ppb.configs.config import DataOutputFiletype

# **PPB24 - Conversion of Battery Measurement Data to a Standardized Format**

[[_TOC_]]

## Description
This project enables you to convert battery measurement data to a standardized format.

Cycler output their measurement data in different formats and different file types, like for example .csv and .xslx. Each has to be handled differently which makes it difficult to work with the data and that's the reason why we created a standardized format.
The standardized Data and Metadata can be used inside of the code and can be output as a .csv (Data), .xlsx (Data) or parquet(Data) to a output_path of your choosing.

Keeping additional data outside of our definition of the standardized columns and custom cycler handling is also possible.


## Standardized Format
The standardized columns are defined as follows:

```python
STANDARD_COLUMNS = [
    "Meta_Data",
    "Step_Count",
    "Voltage[V]",
    "Current[A]",
    "Temperature[°C]",
    "Test_Time[s]",
    "Date_Time",
    "EIS_f[Hz]",
    "EIS_Z_Real[Ohm]",
    "EIS_Z_Imag[Ohm]",
    "EIS_DC[A]"
]
```

## Metadata
Currently, metadata is not standardized. It contains all additional information from the provided measurement file and is stored as a string in the first row of the `Meta_Data` column.

## Supported Cyclers
PyDPEET supports conversion from the following cyclers:
- Arbin
- BaSyTec
- Digatron
- Neware
- Parstat
- Safion
- Zahner

## Installation

### For Development
To contribute to the project, clone the repository:

![Open Project](Pictures ReadMe/Open%20Project.png)

Once cloned, create a new branch for your work:

![New Branch](Pictures ReadMe/New%20Branch.png)

### Requirements
As a maintainer, all requirements should be installed to be able to use, develop, test, and document the project.

All requirememnts can be found in:
        
    ./requirements.dev.txt

Test first, if pip is already installed on your System or virtual environment. Open the commandline (cmd on windows or Terminal on macOS) and type in: 
    
    pip --version

if the pip command gives an Error, try pip3 --version instead:

    pip3 --version 

if that didn´t help either, try installing pip now. 
For that just put python3 get-pip.py into the command line

windows:    

    py -m ensurepip --upgrade

any Linux or macOS: 

    python -m ensurepip --upgrade

It could be, that your pip didn´t get embedded into your system correctly. There are multiple reasons, why that can happen. You can read about it on this Site for Example: 

    https://de.windows-office.net/?p=40510


To install all the requirements run:
        
    pip install -r requirements.dev.txt

To update the list of requirements, if a new lib was added, run:
        
    pip freeze > requirements.dev.txt

### Rebuild package for `pip`

Run 

```shell
  python -m build
```
 
in the project root.

That rebuilds the package in the `dist` directory. Push the project then and your changes are installable via pip from gitlab.

### How to renew the documentation after implementing new functions
Windows only: 
To avoid further complication with sphinx, you now have to add the download path to your Environment Variables. 
Press Windows + R and type in sysdm.cpl

    sysdm.cpl

Go to the tab "advanced" and click on the button called "Environment Variables" at the bottom of the page. 
In the top Window you will find a Variable called "Path". Click on that and choose Edit.
After clicking on "New" you have to put in the Path, which leads to \Python\Scripts. It could look something like this: 

    D:\Programs\Python\Scripts

After you´ve done that, you can now continue with the regular use of Sphinx.

In your Commandline navigate to `docs` in the root of the project

First run 

    make clean

to clean the existing documentation

Then run

    make html 

You'll find the documentation in

    docs/build/html

`index.html` is the root of the documentation


### For Usage
To install PyDPEET in your project, run the following command in your console:

```bash
pip install git+https://oauth2:GITLAB_ACCESS_TOKEN@git.tu-berlin.de/eet/ppb/ppb24.git
```

This will install the package from the main branch.

Replace GITLAB_ACCESS_TOKEN with your actual access token.
You can find or create your token (with read_repository access!) [here](https://git.tu-berlin.de/-/user_settings/personal_access_tokens): 

![img_2.png](Pictures ReadMe/Token.png)

## Usage
To convert a battery measurement file into the standardized format, use:

```python
from ppb.configs.config import Config
from ppb.convert import convert

input_file = "data/raw_measurement.csv"

data_frame = convert(
    config=Config.BaSyTec,
    input_path=input_file,
    keep_all_additional_data=False,
    custom_folder_path=None
)
```

- **`config`** – Specifies which cycler is being used.  
  *Tip: Typing `"config = Configs."` in some IDEs will suggest a list of currently implemented cyclers.*  

- **`input_path`** – Defines the location of the measurement file.  
  *Only supports single files. To convert an entire folder, use `directory_standardization()` or write custom code to parse file paths and pass them to the `convert` function.*  

- **`keep_all_additional_data`** – When set to `True`, retains non-standard data.  
  *Defaults to `False`, keeping only standardized data.*  

- **`custom_folder_path`** – Allows loading custom handling for new or different cyclers.  
  *The folder must contain `reader.py`, `mapper.py`, and `formatter.py`. More details after the examples.*  

- **`return_type`** – returns a `pandas.DataFrame` object.  


Here is a visualization of the Output of this convert using PyCharm IDE:
![alt text](Pictures%20ReadMe/Example%20for%20converting%20a%20BaSyTec%20measurement%20to%20use%20it%20inside%20of%20your%20code.png)

To export a standardized data_frame, use:

```python
from ppb.export import export
from ppb.configs.config import DataOutputFiletype

data_frame = convert(...)
output_path = "output/data/"
output_file_name = "measurement_1"

export(
  data_frame=data_frame,
  output_path=output_path,
  output_file_name=output_file_name,
  data_output_filetype=DataOutputFiletype.csv
)
```
- **`dataFrame`** – The DataFrame to be exported in the specified `data_output_filetype`.

- **`output_path`** – The directory where the standardized measurement file will be created and stored.

- **`output_file_name`** – The name to assign to the exported file.

- **`data_output_filetype`** – The file format to export the data as (e.g., CSV, Parquet, Excel).

The file could look like this when viewed with a csv reader like Excel:
![alt text](Pictures%20ReadMe/Example%20for%20converting%20a%20BaSyTec%20measurement%20and%20saving%20it%20to%20a%20output_path2.png)

To standardize a directory of measurement files, use the `directory_standardization` function:

```python
from ppb.directory_standardization import directory_standardization
from ppb.configs.config import Config, DataOutputFiletype

input_path = "input/data/"
output_path = "output/data/"

directory_standardization(
    config=Config.BaSyTec,
    input_path=input_path,
    output_path=output_path,
    keep_all_additional_data=False,
    custom_folder_path=None,
    data_output_filetype=DataOutputFiletype.parquet
)
```

- **`config`** – Specifies the cycler being used.  
  *Tip: Typing `"config = Configs."` in some IDEs will show a list of implemented cyclers.*

- **`input_path`** – Defines the path to the folder containing the measurement files.

- **`output_path`** – Specifies where to save the standardized measurement files and how to name them.

- **`keep_all_additional_data`** – When set to `True`, retains non-standard data; defaults to `False`, which only includes standardized data.

- **`custom_folder_path`** – Enables loading custom handling for new or different cyclers.  
  *The folder must contain `Reader.py`, `Mapper.py`, and `Formatter.py`.*

- **`data_output_filetype`** – Defines the desired file type for the output file.  
  *Tip: Typing `"data_output_filetype = Data_output_filetype."` will show a list of supported file types.*

The output could look like this:

![img.png](Pictures ReadMe/BaSyTec Folder Output.png)

Naming scheme:

    Originalfilename_Config_Date_Time_OutputFileType

## Custom Handling of Cycler

If a custom `config` is used and a `custom_folder_path` is defined, you can implement your own custom solution.

### Example with the BaSyTec Handling on my local device:

```python
from ppb.convert import convert
from ppb.configs import Config

data_frame = convert(
    config=Config.Custom,
    input_path=r"D:\Downloads\Uni\_Data\_Data\BaSyTec\Basytec145\TC23LFP01_CU_25deg.txt",
    custom_folder_path=r"D:\Test\BaSyTec"
)

###YOUR CODE using the DataFrame
```

The custom folder needs the following files:

![alt text](Pictures%20ReadMe/Custom%20Handling%20of%20Zyklisierer2.png)

The files need to implement the following functions to work with our project:

### Mapper.py Example
```python
# Define the mapping from current names to standardized names (ALL standardized columns need to be in either one!)

COLUMN_MAP = {
    "Time[h]": "Test_Time[s]",
    "U[V]": "Voltage[V]",
    "I[A]": "Current[A]",
    "T1[°C]": "Temperature[°C]",
    "Line": "Step_Count",
}

MISSING_REQUIRED_COLUMNS = [
    "Date_Time",
    "EIS_f[Hz]",
    "EIS_Z_Real[Ohm]",
    "EIS_Z_Imag[Ohm]",
    "EIS_DC[A]"
]
```

It is also possible to define multiple `COLUMN_MAP`'s + `MISSING_REQUIRED_COLUMNS` in a single `Mapper.py`, but if you do you'll have to create another config and set the mapping call in column mapping accordingly. (Step 7. in "How to add a Custom Handling to the Project")



### Formatter.py:
```python
import pandas

def get_data_into_format(dataFrame: pandas.DataFrame):
    ***YOUR CODE***
    return
```

### Reader.py:
```python
import pandas as pd

def to_dataframe(input_path: str) -> (pd.DataFrame, str):
    ***YOUR CODE***
    return dataFrame, metadata_string
```

## How to add a Custom Handling to the Project
0. create a Custom Handling of cycler and test it using the custom config. If you're sure that It works create a new branch from this project

1. add the custom folder to the Zyklisierer folder

![alt_text](Pictures%20ReadMe/How%20to%20add%20a%20Custom%20Handling%20to%20the%20Project0.png)

2. add this `__init__.py` in the folder

![alt_text](Pictures%20ReadMe/How%20to%20add%20a%20Custom%20Handling%20to%20the%20Project1.png)

3. add the new `Config`

![alt_text](Pictures%20ReadMe/How%20to%20add%20a%20Custom%20Handling%20to%20the%20Project2.png)

4. add the reader for the new `Config` to the config_maps

![alt_text](Pictures%20ReadMe/How%20to%20add%20a%20Custom%20Handling%20to%20the%20Project3.png)

5. add the mapper for the new `Config` to the config_maps

![alt_text](Pictures%20ReadMe/How%20to%20add%20a%20Custom%20Handling%20to%20the%20Project4.png)

6. add the formatter for the new `Config` to the config_maps

![alt_text](Pictures%20ReadMe/How%20to%20add%20a%20Custom%20Handling%20to%20the%20Project5.png)

7. don't forget imports

![alt_text](Pictures%20ReadMe/How%20to%20add%20a%20Custom%20Handling%20to%20the%20Project6.png)

## Roadmap + Contributing 
You can see planned features and updates here:
https://git.tu-berlin.de/eet/ppb/ppb24/-/issues/?sort=created_date&state=opened&first_page_size=100

## Authors and acknowledgment
Daniel Schröder (458278) 

Cataldo De Simone (483710)

Alexander Hinrichsen (457492)

Jan Kalisch (455583)

## Support TODO
Support will be defined once published officially.

## License TODO
License will follow once published officially.

## Project status
Will likely be worked on by future groups.