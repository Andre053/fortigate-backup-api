import os
import shutil
from datetime import datetime
import time
from enum import Enum

LOG_DIRECTORY = os.path.join(os.path.expanduser("~"), "programs/fortigate-backup-api/retention_logs")
BACKUP_DIRECTORY = os.path.join("/home/shared", "backups")
DATE = datetime.now().strftime('%m-%d-%Y') # get current date script is being run

class Ret(Enum):
    DAILY = 1
    WEEKLY = 2
    MONTHLY = 3
    YEARLY = 4

def run():
    companies = get_sub_dirs(BACKUP_DIRECTORY)
    create_folders(LOG_DIRECTORY)
    log = create_log()
    
    log.write(f"### {DATE} ###\n")
	
    for c in companies:
        devices = get_sub_dirs(c)
        for dev in devices:
            daily_path = os.path.join(dev, "daily")
            weekly_path = os.path.join(dev, "weekly")
            monthly_path = os.path.join(dev, "monthly")
            yearly_path = os.path.join(dev, "yearly")
            create_folders(daily_path)
            create_folders(weekly_path)
            create_folders(monthly_path)
            create_folders(yearly_path)

            daily_backups = get_sub_dirs(daily_path)
            daily_backup_count = len(daily_backups)

            weekly_backups = get_sub_dirs(weekly_path)
            weekly_backup_count = len(weekly_backups)

            monthly_backups = get_sub_dirs(monthly_path)
            monthly_backup_count = len(monthly_backups)

            yearly_backups = get_sub_dirs(yearly_path)
            yearly_backup_count = len(yearly_backups)
            
            if daily_backup_count > 8:
                log.write(f"Daily backup full for {c} {dev}\n")
                retend_files(Ret.DAILY, daily_backups, weekly_path, log)

            if weekly_backup_count > 4:
                log.write(f"Weekly backup full for {c} {dev}\n")
                retend_files(Ret.WEEKLY, weekly_backups, monthly_path, log)

            if monthly_backup_count > 12:
                log.write(f"Monthly backup full for {c} {dev}\n")
                retend_files(Ret.MONTHLY, monthly_backups, yearly_path, log)                

            if yearly_backup_count > 3:
                log.write(f"Yearly backup over 3 for {c} {dev}\n")
	
# returns list of complete paths
def get_sub_dirs(path):
    return [x.path for x in os.scandir(path) if x.is_dir()]
	
def delete_files_in_list(files):
    for f in files:
        try:
            shutil.rmtree(f)
        except OSError as e:
            print("Error: %s - %s", e.filename, e.strerror)
    
def move(src, dst):
    shutil.move(src, dst)
	
def retend_files(ret_period, files, dst_path, log):

    # youngest to oldest
    f_sorted = sorted(files, key=lambda x: datetime.strptime(os.path.basename(x), "%m-%d-%Y"), reverse=True) 
	
    # keep previous 7 days, move the 8th, dispose of rest
    if ret_period == Ret.DAILY:
        
        to_move = f_sorted[7]
        to_del = f_sorted[8:]
        
        move(to_move, dst_path)
        delete_files_in_list(to_del)
        
	
    elif ret_period == Ret.WEEKLY:
        to_move = f_sorted[0]
        to_del = f_sorted[1:]
        
        move(to_move, dst_path)
        delete_files_in_list(to_del)
	
    elif ret_period == Ret.MONTHLY:
        to_move = f_sorted[0]
        to_del = f_sorted[1:]
        
        move(to_move, dst_path)
        delete_files_in_list(to_del)
       
    log.write(f"Moved {os.path.basename(to_move)}\n")

def create_log():
    try:
        return open(os.path.join(LOG_DIRECTORY, f"bkp-ret-{DATE}"), "a")
    except Exception as e:
        print(f"Error creating log file {e}")
        sys.exit()
		
def create_folders(path):
    if not os.path.exists(path): os.makedirs(path)

def main():
    run()
	
if __name__ == '__main__':
    main()
