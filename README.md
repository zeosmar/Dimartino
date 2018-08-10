# COINS_images2bids

COINS_BIDS.py - Get the successfully ran scan numbers and save in a .csv file.

syntax - 

COINS_BIDS.py -rs (input runsheet name with path {path not required if runsheet present in current directory}) -ks (input keysheet name with path {path not required if keysheet present in current directory}) -op (input output file name with path {path not required if output is to be saved in current directory}) 

or

COINS_BIDS.py --runsheet (input runsheet name with path {path not required if runsheet present in current directory}) --keysheet (input keysheet name with path {path not required if keysheet present in current directory}) --output (input output file name with path {path not required if output is to be saved in current directory})

batch_dcm2bids.py - Organize the data into BIDS format.

syntax - 

batch_dcm2bids.py --source (input the source directory path containing the subject folders , if no path is given the current directory is taken as source directory) --destination (input the destination directory , if no path is given the current directory is taken as the destination directory) --COINS_BIDS (input the COINS .csv file with successful scan information with its path, if not path is given the current directory is taken as the input path for the COins .csv file)
