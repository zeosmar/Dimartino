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

if fail:
    print('Test failed')
elif not os.path.exists(os.path.join(directory, 'working', 'COINS_out.csv')):
    print('Test failed')
else:
    print('Test succeeded')


 
