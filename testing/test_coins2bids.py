import os, sys

fail = False

directory = os.getcwd()

code_directory, tail = os.path.split(directory)

COINS_BIDS_dir = os.path.join(code_directory, 'COINS-images2bids', 'COINS_BIDS.py')

cmd = 'python {} -rs {} -ks {} -op {}'.format(COINS_BIDS_dir, os.path.join(directory, 'working', 'COINS_run_sheet_output.csv'), os.path.join(code_directory, 'COINS-images2bids', 'COINS_run_sheet_key.csv'), os.path.join(directory, 'working', 'COINS_out.csv'))

try:
    os.system(cmd)
except:
    fail = True

coins2bids_dir = os.path.join(code_directory, 'COINS-images2bids', 'coins2bids.py')

cmd = 'python {} --COINS_BIDS {} --temp_json {} --input_path {}'.format(coins2bids_dir, os.path.join(directory, 'working', 'COINS_out.csv'), os.path.join(code_directory, 'COINS-images2bids', 'config_new2.json'), os.path.join(directory, 'working', 'diicom_source'))

try:
    os.system(cmd)
except:
   fail = True

if fail:
    print('Test failed')
elif not os.path.exists(os.path.join(directory, 'working', 'COINS_out.csv')):
    print('Test failed on COINS_BIDS')
elif not os.path.exists(os.path.join(directory, 'working', 'diicom_source', 'sub-80125', '80125.json')):
    print('Test failed on coins2bids')
else:
    print('Test succeeded')


 
