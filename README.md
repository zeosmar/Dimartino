# proc-biopac-coins
Basic script for processing acq files for use in BIDS formated fMRI datasets.
Also creates some basic QA and summary stats. The main feature of this version is the integration of the physio processing with the coins run sheet outputs. 

---
### Getting Started
---
#### How to get it

You can clone from git
```
git@github.com:none2serious/proc-biopac-coins.git
```
or just download directly:

![Just Download](https://github.com/none2serious/proc-biopac-coins/blob/master/download.png)

#### Installation
Copy the proc_biopac.py and physio_libs.py files into the same folder somewhere in your path. I think that you have been putting it in the project directory, but it could go anywhere so long as the two files are in the same folder.

#### Assumptions
This version assumes that for each dataset you have already created the physio template using the coins conversion script. It also assumes that you have successfully run dcm2bids, creating the BIDS folder structure for each dataset.

### How to use it
---
The help file for the script:
```
usage: proc_biopac_coins [-h] -project PROJECT_DIRECTORY [-sublist SUBJECT_LIST]
                   [-templates TEMPLATE_DIRECTORY]

optional arguments:
  -h, --help            show this help message and exit
  -project PROJECT_DIRECTORY, --project_directory PROJECT_DIRECTORY
                        The project folder containing sourceData, etc.
                        (Required)
  -sublist SUBJECT_LIST, --subject_list SUBJECT_LIST
                        File name listing subjects to process; defaults to
                        'subject_list.txt' in the working directory.
  -templates TEMPLATE_DIRECTORY, --template_directory TEMPLATE_DIRECTORY
                        Directory for physio templates; defaults to
                        'physio_templates' in project dir
```
#### Project Directory
In most cases, you will only need to provide the toplevel directory for the project (the one containing originals, BIDS, etc.)
#### Subject List
You will need to provide a file containing a list of subject IDs. By default, the program will read in 'subject_lists.txt' from the working directory. If you created a different file to hold the list, provide it here.
#### Template Directory
It is possible to also provide the path to the folder holding the physio templates. However, by default the physio templates will have been created in the "physio_templates" folder within the project directory. You will only need to provide the -templates argument in the unlikely case that the physio templates are saved somewhere else. 





