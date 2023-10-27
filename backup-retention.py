import os
import time
import shutil

# check folders once a week to organize retention
# for each company, each device
# save last 7 days, last 4 weeks, last 4 months, last 2 semi-anually, last year

BACKUP_FOLDER = os.path.join(os.path.expanduser("~"), "backups")

def main():
	companies = get_sub_dirs(BACKUP_FOLDER)

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
			if daily_backup_count > 7:
				newest_daily = newest_oldest(daily_path)	
				move_backup(newest_daily, dev, "weekly") 
				delete_oldest(newest_daily, 0)

			if weekly_backup_count > 4:
				newest_weekly = gather_newest(weekly_path)
				move_backup(newest_weekly, dev, "monthly")	
				delete_oldest(newest_weekly, 0)

			if monthly_backup_count > 12:
				newest_monthly = gather_newest(monthly_path)
				move_backup(newest_monthly, dev, "yearly")
				delete_oldest(newest_monthly, 0)

			if yearly_backup_count > 1:
				newest_yearly = gather_newest(yearly_path)
				os.remove(newest_yearly)
				delete_oldest(newest_yearly, 3)

def delete_oldest(folder, leftover):
	while len(os.listdir(folder)) > leftover:
		oldest = gather_oldest(folder)	
		os.remove(oldest)


def gather_oldest(folder):
	t_old = time.time()

	for backup in folder:
		t = os.stat(backup).st_ctime
		if t < t_old: 
			t_old = t
			oldest = backup
	return oldest

def gather_newest(folder):
	t_new = gather_oldest(folder)

	for backup in folder:
		t = os.stat(backup).st_ctime)
		if t > t_new:
			t_new = t
			newest = backup
	return newest 

# dev destination is location of dev folder, 
def move_backup(src, dev_dst, timeframe):
	target = os.path.join(dev_dst, timeframe)	
	create_folders(target)
	print("Saving to:", target)
	shutil.move(os.listdir(oldest)[0], target) 
	
def create_folders(path):
	if not os.path.exists(path): os.makedirs(path)

def get_sub_dirs(path):
	return [x.path for x in os.scandir(path) if x.is_dir()]

if __name__ == '__main__':
	main()
