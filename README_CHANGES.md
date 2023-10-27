# BALANCED+ Programmatic Backups

- Builds on the original scripts to be better organized for multiple companies
	- Adds initial column in CSV for companies
	- Using sendgrid API in automatic to notify when backups fail
- Automated and manual versions (renamed)
- Retention script
	- When daily/weekly/monthly/yearly backup count reached, the oldest are cleared and moved to the next timeframe of backup
- Create your own fortigates.csv file
- Creates backups in your home directory
