# Dimartino

Environment: Python 2.7

Dependencies: 
python : numpy pandas matplotlib json argparse bioread dcm2bids
cmd : dcm2niix edf2asc

1) COINS-images2bids/COINS_BIDS_setup.py : pulls relevant information from COINS runsheet and prepares for dcm2bids
  --runsheet /Path/to/COINS/runsheet
  --keysheet /Path/to/COINS/keysheet (COINS-images2bids/COINS_run_sheet_key.csv)
  --temp_json /Path/to/config.json (COINS-images2bids/config.json)
  --sub_dir /Path/to/subject/source/directory 
  
2) COINS-images2bids/batch_dcm2bids.py : converts scan diicoms to nifti, outputs in BIDS format
  --source /Path/to/subject/source/directory (or single subject directory)
  --destination /Path/to/bids/folder 
  --COINS_BIDS /Path/to/selectedscans.csv (step 1 output)
  
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