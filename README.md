# Environment Installation

Environment: Python 2.7

Dependencies: 
python : numpy pandas matplotlib json argparse bioread dcm2bids
cmd : dcm2niix edf2asc


**Using the command line**

1) conda create --name [name] --file [/Path/to/requirements.txt]
	*where 'name' is the name you would like to give your environment
	*where '/Path/to/requirements.txt' is the path to requirements.txt, downloaded
		from github

2) conda activate [name] 
	*where 'name' is the name you gave your environment in step 1

	*if command line throws an error during this step, try instead using
		source activate [name]

3) pip install bioread dcm2bids argparse

4) dcm2niix
	*if the command line does not know what this command is, follow instructions
		here to add dcm2niix to your command environment
	*if the command line produces usage instructions (e.g. examples), continue to next step

**Additional**

5) Move the file edf2asc (downloaded from github) to the following directory:
	[/Path/to/Anaconda/Folder]/envs/[name]/bin
	*where 'Path/to/Anaconda/Folder is the path to the anaconda source folder
	*where 'name' is the name you gave your environment in step	1

# Script Instructions

1) COINS-images2bids/COINS_BIDS_setup.py : pulls relevant information from COINS runsheet and prepares for dcm2bids
  --runsheet /Path/to/COINS/runsheet
  --keysheet /Path/to/COINS/keysheet (COINS-images2bids/COINS_run_sheet_key.csv)
  --temp_json /Path/to/config.json (COINS-images2bids/config.json)
  --sub_dir /Path/to/subject/source/directory 
  
  *needed for input: 
    COINS runsheet
    keysheet (downloaded from github)
    model json file (downloaded from github)
    a folder containing diicom data
  *output: 
    sub_dir/selected_scans.txt - contains file names of good scan runs for each subject, based on COINS sheet
    sub_dir/selected_physio.txt - contains file names of good physio data for each subject, based on COINS sheet
    sub_dir/selected_track.txt - contains file names of good tracking data for each subject, based on COINS sheet
    sub_dir/[subID]/[subID].json - contains file names of good scan runs for the subject, based on COINS sheet
    sub_dir/error_log.txt - a text file listing any subjects from the COINS sheet that did not compile correctly
      *most common is 'subject not in source folder' - just indicates that your sub_dir did not contain diicom data for a particular subject, does not indicate malfunctioning code, does not cause a problem with the output produced from other subjects
  
2) COINS-images2bids/batch_dcm2bids.py : converts scan diicoms to nifti, outputs in BIDS format
  --source /Path/to/subject/source/directory (or single subject directory)
  --destination /Path/to/bids/folder 
  --COINS_BIDS /Path/to/selected_scans.csv (step 1 output)
  
3) COINS2physio/COINS_physio.py : generates jsons for physio processing
  --runsheet /Path/to/selectedphysio.csv (step 1 output)
  --input_dir /Path/to/source/directory
  --temp_json /Path/to/physio-template.json (COINS2physio/physio-template.json)
  
4) proc-biopac-COINS/proc_biopac_coins.py : process and QC physio data
  --project_directory /Path/to/source/directory
  --subject_list /Path/to/list/of/subjects/to/process
  --template_directory /Path/to/template/directory (step 3 output)
  -bids_dir /Path/to/BIDS/directory

5) COINS2tracking/COINS_tracking.py : generates jsons for tracking data
  --runsheet /Path/to/selected_track.csv (step 1 output)
  --input_dir /Path/to/source/directory
  --temp_json /Path/to/tracking-template.json (COINS2tracking/tracking-template.json)

**Ensure that .edf files are in 01+eyeTracking within the diicom structure and not in a zipped file

6) proc-tracking-COINS/proc-tracking-COINS.py : processes and QCs eye tracking
  --project_directory /Path/to/source/directory
  --subject_list /Path/to/list/of/subjects/to/run
  --template_directory /Path/to/template/directory (step 5 output)
  -bids_dir /Path/to/BIDS/directory
  
7) eprime-codes/batch_ce.py : generates csv files from eprime output
  EITHER
  --path /Path/to/source/directory
  OR
  --subjectID /Path/to/single/subject/directory
  
8) eprime-codes/csv2tsv.py : converts csvs from step 7 to tsvs, puts in BIDS format
  --output_dir /Path/to/bids/directory
  EITHER
  --input_dir /Path/to/subject/source/folder
  OR
  --subID /Path/to/single/subject/folder
  
9) eprime-codes/feat_excel.py : generates feat onset vectors
  --output_dir /Path/to/bids/directory
  EITHER
  --input_dir /Path/to/subject/source/directory
  OR
  --subjectID /Path/to/single/subject/directory

10) final-bids/finalize_bids.py : combines runs from same subject into single file
  --inputdir /Path/to/bids/directory