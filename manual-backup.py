import os
import csv
import sys
import requests
import smtplib
from email.message import EmailMessage
from datetime import datetime

# The req object is used to make https requests
req = requests.session()

# Uncomment these two lines below to disable SSL certificate warnings
requests.packages.urllib3.disable_warnings()
req.verify = False

# Global variables
DATE = datetime.now().strftime('%m-%d-%Y')      # Today's date in the format mm-dd-yyyy
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__)) 					# PATH to current directory, used for getting csv
HOME_DIR = os.path.expanduser('~')   				# Path to the home directory
BKP_FOLDER = os.path.join(HOME_DIR, 'backups')     # Path to the backups folder
LOGS_FOLDER = os.path.join(CURRENT_DIR, 'logs')     # Path to the logs folder
online_ip, error_message = '',''
bkp_fail = []

def main():
    # Read the fortigates.csv file
    all_fortigates = read_fortigates()
    
    # Create folders for backups and logs if they don't exist
    create_folders(LOGS_FOLDER)

    # Create log file
    log = create_log()
    log.write(f'Backup log - {DATE}\n')
		
    fortigates = select_fortigates(all_fortigates)

    # Backup each Fortigate
    for fgt in fortigates:

        # Clear error_message variable before each backup
        global error_message
        error_message = ''
        
        print('\n========================================')
        print(f'Fortigate: {fgt["company"]} {fgt["name"]}')

        log.write('\n========================================\n')
        log.write(f'Fortigate: {fgt["company"]} {fgt["name"]}\n')
        
        # Call the main backup function
        bkp_ok = backup(fgt)

        # Check if the backup was successful
        if bkp_ok:
            print('Backup successful!')
            log.write(f'Fortigate online on IP: {online_ip}\n')
            log.write('Backup successful!\n')

        # If not, check if the Fortigate is offline or if there was an error
        else:
            if online_ip == '':
                print('Fortigate offline!')
                log.write('Fortigate offline!\n')

            elif error_message != '':
                print(f'Error message: {error_message}')
                log.write(f'Error message: {error_message}\n')

            print('Backup failed!')
            log.write('Backup failed!\n')
            bkp_fail.append(fgt['name'])

        print('========================================\n')
        log.write('========================================\n')
    
    # Print the list of failed backups if there are any
    if len(bkp_fail) > 0:
        print('List of failed backups:')
        log.write('\nList of failed backups:\n')
        for fgt in bkp_fail:
            print(fgt)
            log.write(f'{fgt}\n')
        
        print(f'\nCount: {len(bkp_fail)}\n')
        log.write(f'\nCount: {len(bkp_fail)}\n')

    log.close()
    print('Backup finished!')
    input('Press ENTER to exit...')
    sys.exit()

def read_fortigates():

    try:
        # Read the fortigates.csv file and convert it to a list of dictionaries
        with open(os.path.join(CURRENT_DIR, 'fortigates.csv'), 'r') as file:
            fortigates = list(csv.DictReader(file, delimiter=','))
    except FileNotFoundError as e:
        print(f'File fortigates.csv not found: {e}')
        input('Press ENTER to exit...')
        sys.exit()
    except Exception as e:
        print(f'Error reading fortigates.csv file: {e}')
        input('Press ENTER to exit...')
        sys.exit()

    return fortigates

def create_folders(path):

    try:
        # Create the backups and logs folders if they don't exist
        # exist_ok=True prevents the function from raising an exception if the folder already exists
        os.makedirs(path, exist_ok=True)
    except Exception as e:
        print(f'Error creating folders: {e}')
        input('Press ENTER to exit...')
        sys.exit()

def create_log():
    
    try:
        # Create log file and remain it open to write
        return open(os.path.join(LOGS_FOLDER, f'bkp-{DATE}.log'), 'a')
    except Exception as e:
        print(f'Error creating the log file: {e}')
        input('Press ENTER to exit...')
        sys.exit()

def backup(fgt):

    # Mount the backup URL
    url = mount_url(fgt)
    if not url: return False

    # Perform the backup
    print(f'Fortigate online on {online_ip}, backing up...')
    try:
        bkp_data = req.get(url)
    except Exception as e:
        global error_message
        error_message = str(e)
        return False

    # Save and check the backup file
    file_ok = save_and_check_file(fgt['company'], fgt['name'], bkp_data)
    return file_ok

def ping(ip):

    # Do a simple request to the Fortigate to check if it is online
    try:
        req.get(f'https://{ip}', timeout=3)
        return True
    except:
        return False

def check_online_ip(fgt):

    # Access the global variable online_ip
    global online_ip

    # Check if the Fortigate is online on primary IP
    if ping(fgt['ip_1']):
        online_ip = fgt['ip_1']
        return online_ip
    
    # If not, check if the Fortigate has a secondary IP and if it is online
    elif fgt['ip_2'] != '' and ping(fgt['ip_2']):
        online_ip = fgt['ip_2']
        return online_ip
    
    # If the Fortigate is not available on any IP, return False
    online_ip = ''
    return False

def mount_url(fgt):

    # URI to backup the Fortigate
    URI = '/api/v2/monitor/system/config/backup?scope=global&access_token='

    # Check if the Fortigate is online on both IPs
    is_online = check_online_ip(fgt)
    if is_online:
        # If it is online, mount the URL to backup the Fortigate
        return f'https://{is_online}{URI}{fgt["token"]}'
    else:
        return ''
    
def save_and_check_file(company, name, data):

    # Access the global variable error_message
    global error_message

    # Path to the backup file
    folder_path = os.path.join(BKP_FOLDER, company, name, "daily", DATE)
		
    create_folders(folder_path)
    file_path = os.path.join(folder_path, f'{name}-bkp={DATE}.conf')
    try:
        # Save the backup data to a file
        with open(file_path, 'wb') as file:
            for line in data:
                file.write(line)

        # Check if the file is a valid Fortigate configuration file
        with open(file_path, 'r') as file:
            first_line = file.readline()
            if first_line.startswith('#config'):
                return True
        
        # If the file is not valid, delete it and change the error_message variable
        os.remove(file_path)
        error_message = 'Invalid backup file'
        return False
    
    except Exception as e:
        error_message = str(e)
        return False

def select_fortigates(fgs):
    # display all companies
    for i in range(0, len(fgs), 2):
        # Print only one Fortigate on the last line if the number of Fortigates is odd
        # This prevents a list index out of range error
        if i == len(fgs) - 1:
            print(f'{i:3} - {fgs[i]["name"]}')
            break
        else:
            print(f'{i:3} - {fgs[i]["name"]:<40} {i+1:2} - {fgs[i+1]["name"]}')
    print(f'all - {"All Fortigates":<38} exit - Close the program')
    return [fgs[x] for x in get_fortigates(fgs)]

def get_fortigates(fortigates):
    # Ask the user to select the Fortigates to backup
    # The user can select multiple Fortigates by typing the numbers separated by commas
    # The user can also type 'all' to backup all Fortigates
    # Check if the user input is valid, not empty and the values are on the range of the Fortigates list
    while True:
        try:
            selected = input('\nSelect the Fortigates to backup (separated by commas): ')

            # Check if the user typed 'all' to backup all Fortigates
            if selected.lower() == 'all': return list(range(len(fortigates)))

            # Check if the user typed 'exit' to exit the script
            elif selected.lower() == 'exit': sys.exit()

            # Check if the user typed nothing
            elif not selected:
                print('No input, try again.')
                continue

            # Split the string into a list of numbers
            else:
                selected = [int(i) for i in selected.split(',')]

                # Check if the numbers are on the range of the Fortigates list
                if not all(i in range(len(fortigates)) for i in selected): raise ValueError

                return selected

        except ValueError:
            print('Invalid input, try again.')
            continue

 
if __name__ == '__main__':
    main()

