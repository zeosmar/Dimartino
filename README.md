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

4) conda install -c conda-forge dcm2niix


**Additional**

5) Move the file edf2asc (provided via email) to the following directory:
	[/Path/to/Anaconda/Folder]/envs/[name]/bin
	* where 'Path/to/Anaconda/Folder is the path to the anaconda source folder
	* where 'name' is the name you gave your environment in step 1

# Script Instructions

1) COINS-images2bids/COINS_BIDS_setup.py : pulls relevant information from COINS runsheet and prepares for dcm2bids
  * arguments
    * --runsheet /Path/to/COINS/runsheet
    * --keysheet /Path/to/COINS/keysheet (COINS-images2bids/COINS_run_sheet_key.csv)
    * --temp_json /Path/to/config.json (COINS-images2bids/config.json)
    * --sub_dir /Path/to/subject/source/directory 
  * needed for input: 
    * COINS runsheet
    * keysheet (downloaded from github)
    * model json file (downloaded from github)
    * a folder containing diicom data
  * output: 
    * sub_dir/selected_scans.txt - contains file names of good scan runs for each subject, based on COINS sheet
    * sub_dir/selected_physio.txt - contains file names of good physio data for each subject, based on COINS sheet
    * sub_dir/selected_track.txt - contains file names of good tracking data for each subject, based on COINS sheet
    * sub_dir/[subID]/[subID].json - contains file names of good scan runs for the subject, based on COINS sheet
    * sub_dir/error_log.txt - a text file listing any subjects from the COINS sheet that did not compile correctly
      * most common is 'subject not in source folder' - just indicates that your sub_dir did not contain diicom data for a particular subject, does not indicate malfunctioning code, does not cause a problem with the output produced from other subjects
  
2) COINS-images2bids/batch_dcm2bids.py : converts scan diicoms to nifti, outputs in BIDS format
  * arguments
    * --source /Path/to/subject/source/directory (or single subject directory)
    * --destination /Path/to/bids/folder 
    * --COINS_BIDS /Path/to/selected_scans.csv (step 1 output)
  * needed for input
    * selected_scans.csv (step one output)
    * a folder containing diicom data
    * a destination folder for the sorted bids data (if you give a path in --destination that does not already exist, it will be created)
  * output
    * destination - contains scan data organized in bids format (note: at this stage, participants with multiple sessions, e.g. sub-80084 and sub-80084b, are treated as separate subjects. They will be combined in a later step.)
    * source/error_log.txt - a text file listing any subjects from the COINS sheet that did not compile correctly
      * most common is 'subject not in source folder' - just indicates that your sub_dir did not contain diicom data for a particular subject, does not indicate malfunctioning code, does not cause a problem with the output produced from other subjects
      * this information is appended to the error log from step 1 - if a participant threw an error in step 1, they will appear a second time in this step
  
3) COINS2physio/COINS_physio.py : generates jsons for physio processing
  * arguments
    * --runsheet /Path/to/selectedphysio.csv (step 1 output)
    * --input_dir /Path/to/source/directory
    * --temp_json /Path/to/physio-template.json (COINS2physio/physio-template.json)
  * needed for input
    * selectedphysio.csv - produced in step 1
    * folder containing diicom data
    * COINS2physio/physio-template.json - downloaded from github
  * output
    * input_dir/physio-templates - a folder containing a json that details the file names for the good physio runs for each participant
    * COINS2physio/errorlog.txt - a list of subjects whose physio data did not compile/QC correctly. 
      * This is distinct from the error_log.txt in steps 1 and 2. Information does not append to the original error log, and this error log is located in the code source folder.
  
4) proc-biopac-COINS/proc_biopac_coins.py : process and QC physio data
  * arguments
    * --project_directory /Path/to/source/directory
    * --subject_list /Path/to/list/of/subjects/to/process
    * --template_directory /Path/to/template/directory (step 3 output)
    * --bids_dir /Path/to/BIDS/directory
  * needed for input
    * folder with diicom data (esp. 01+physio)
    * a list of subjects to process (.txt file, formatted 'sub-80084', one subject per line)
    * folder with physio jsons for each subject (output from step 3)
    * a destination folder for bids output (should be the same as given in step 2)
  * output
    * project_directory/[sub_ID]/QC/physio - a directory for each subject containing physio QC information and images
    * bids_dir/[sub_ID]/func/[].tsv - a .tsv file with the time course of the physio data, in bids format
    * project_directory/physio_values.csv - a list of relevant physio values extracted from the data (including heart rate, respiration rate, etc)

5) COINS2tracking/COINS_tracking.py : generates jsons for tracking data
  * arguments
    * --runsheet /Path/to/selected_track.csv (step 1 output)
    * --input_dir /Path/to/source/directory
    * --temp_json /Path/to/tracking-template.json (COINS2tracking/tracking-template.json)
  * needed for input
    * selected_track.csv (output from step 1)
    * folder with diicom data
    * COINS2tracking/tracking-template.json - downloaded from github
  * output
    * input_dir/tracking-templates - folder with json containing file names for good eye tracking runs for each subject
    * COINS2tracking/error_log.txt - list of subjects whose eye tracking data fails to compile

6) proc-tracking-COINS/proc-tracking-COINS.py : processes and QCs eye tracking
  * arguments
    * --project_directory /Path/to/source/directory
    * --subject_list /Path/to/list/of/subjects/to/run
    * --template_directory /Path/to/template/directory (step 5 output)
    * --bids_dir /Path/to/BIDS/directory
  * needed for input
    * folder with diicom data
    * list of subjects to process (.txt file, formatted 'sub-80084', one subject per line)
    * folder with jsons containing file names for good eye tracking runs (step 5 output)
    * bids formatted destination folder (should be same as given in step 4 and step 2)
  * output
    * project_directory/[subid]/QC/eyetracking - folder containing QC info and images for eye tracking data
    * bids_dir/[subid]/func/[].tsv - .tsv file with time series for eye tracking data
  
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