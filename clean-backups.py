import os
import time
import shutil
from datetime import datetime

# check folders once a week to organize retention
# for each company, each device
# save last 7 days, last 4 weeks, last 4 months, last 2 semi-anually, last year

LOG_DIRECTORY = os.path.join(os.path.expanduser("~"), "programs/fortigate-backup-api/retention_logs")
BACKUP_FOLDER = os.path.join(os.path.expanduser("~"), "backups")
DATE = datetime.now().strftime('%m-%d-%Y') # get current date script is being run

def main():
    companies = get_sub_dirs(BACKUP_FOLDER)
    create_folders(LOG_DIRECTORY)
    log = create_log()
    # loop through companies and devices
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

            # take the weekly backup, get the oldest backup
            if daily_backup_count > 14:
                log.write(f"Daily backup full for {c} {dev}\n")
                retend_move(daily_path, weekly_path, 7)

            if weekly_backup_count > 4:
                log.write(f"Weekly backup full for {c} {dev}\n")
                retend_move(weekly_path, monthly_path, None)

            if monthly_backup_count > 12:
                log.write(f"Monthly backup full for {c} {dev}\n")
                retend_move(monthly_path, yearly_path, None)
            if yearly_backup_count > 3:
                log.write(f"Yearly backup over 3 for {c} {dev}\n")
    
# moves newest file to dst
def retend_move(src, dst, dlt_count):
    
    # files map uses time as key, tuple with (file, file_dir)
    files_map, times = get_files_and_timestamps(src)
    if len(times) == 0: exit("Failure retend move")
    to_delete = [files_map[time][0] for time in times[1:]] # ignore the first file
    to_delete_dirs = [files_map[time][1] for time in times[1:]] # ignore the first file
    to_move = [files_map[times[0]][1]] # want to move the whole directory
    if dlt_count != None:
        to_delete = to_delete[dlt_count:]
        to_delete_dirs = to_delete_dirs[dlt_count:]
        to_move = [files_map[times[dlt_count]][1]]

    move_files(to_move, dst)
    delete_files(to_delete)
    delete_dirs(to_delete_dirs)

def delete_dirs(dirs):
    for d in dirs:
        os.rmdir(d)

def delete_files(files):
    for f in files:
        os.remove(f)

# list of folders which should have backups inside
def get_files(d):
    files = []
    dirs = [os.path.join(d, fd) for fd in os.listdir(d)]
    for d in dirs:
        f = os.listdir(d)
        # remove empty dirs
        if len(f) == 0: os.rmdir(d); print("Removed empty dict", d)
        else: 
            file = os.path.join(d, f[0])
            files.append(file) # should be one file
    return files, dirs 

def get_files_and_timestamps(d):
    # gather all files within the directory
    files, file_dirs = get_files(d)

    # subdirectories have a file inside
    times = [os.path.getmtime(f) for f in files]
    if len(files) != len(times): exit()

    # map holds time as key, then the file path, and the file dir path
    files_map = {times[i]:(files[i], file_dirs[i]) for i in range(len(files))}
    # order times, pick the top 5, remove the rest
    times.sort(reverse=True)
    return files_map, times

def create_log():
    try:
        return open(os.path.join(LOG_DIRECTORY, f"bkp-ret-{DATE}"), "a")
    except Exception as e:
        print(f"Error creating log file {e}")
        sys.exit()

def move_files(files, dst):
    for f in files:
        target = os.path.join(dst, os.path.basename(f))

        create_folders(target)
        shutil.move(src, target)
        print("Moved", f, "to", target)
        

def create_folders(path):
    if not os.path.exists(path): os.makedirs(path)

def get_sub_dirs(path):
    return [x.path for x in os.scandir(path) if x.is_dir()]



if __name__ == '__main__':
    main()
