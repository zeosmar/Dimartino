# COINS2physio
create .json files for biopac physio data analysis form COINS runsheet
syntax -
COINS2physio.py --runsheet="/home/sray/Desktop/physio/COINS_run_sheet_output.csv" --input_dir="/home/sray/Desktop/physio/" --temp_json="/home/sray/Desktop/physio/physio-template.json"
runsheet= path to the COINS runsheet .csv file
input_dir= input directory to the subject files. The final putput is stored in physio directory with the subID.json extension
temp_json= path to the template .json file
