import os

def main():
	RETENTION = 5 # keep 5 copies

	logs = "/home/administrator/programs/fortigate-backup-api/logs"
	retention_logs = "/home/administrator/programs/fortigate-backup-api/retention_logs"

	retend(logs, RETENTION)
	
def retend(p, ret):
	files_map, times = get_files_and_timestamps(p)
	to_delete = [files_map[time] for time in times[ret:]]
	delete_files(to_delete)
	
def delete_files(files):
	for f in files:
		os.remove(f)

def get_files_and_timestamps(d):
	# gather all files within the directory
	files = [os.path.join(d, f) for f in os.listdir(d) if os.path.isfile(os.path.join(d, f))]
	times = [os.path.getmtime(f) for f in files]
	files_map = {times[i]:files[i] for i in range(len(files))}
	# order times, pick the top 5, remove the rest
	times.sort(reverse=True)

	return files_map, times

main()
   
	 
