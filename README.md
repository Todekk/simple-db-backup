# Simple MySQL Backup

This project creates compressed SQL exports of the databases on a local MySQL
or MariaDB server. It is designed for a local XAMPP installation on Windows.

Each run:

1. Finds the databases on the configured MySQL server.
2. Skips the databases listed in `excluded_databases`.
3. Exports each remaining database as a compressed `.sql.gz` file.
4. Stores the exports inside a folder named with the current date.
5. Deletes exports older than the configured retention period.
6. Writes the result to `logs/backup.log`.

## Project Files

- `backup.py` runs the backup.
- `config.json` contains the MySQL connection, backup location, and retention settings.
- `manual-backup.bat` runs a backup manually.
- `logs/backup.log` records successful backups and errors.

## Setup

### 1. Configure `config.json`

Open `config.json` and update its values for your system:

```json
{
  "mysql_bin_dir": "C:/xampp/mysql/bin",
  "mysql_host": "127.0.0.1",
  "mysql_port": 3306,
  "mysql_user": "root",
  "mysql_password": "",
  "backup_dir": "E:/EXAMPLE/backups",
  "retention_days": 30,
  "excluded_databases": [
    "information_schema",
    "performance_schema",
    "mysql",
    "sys",
    "phpmyadmin"
  ]
}
```

Change the following values when needed:

- `mysql_bin_dir`: Path to XAMPP's MySQL executable folder. The default XAMPP path is usually `C:/xampp/mysql/bin`. This folder must contain `mysql.exe` and `mysqldump.exe`.
- `mysql_host`: MySQL server address. Keep `127.0.0.1` for a normal local XAMPP installation.
- `mysql_port`: MySQL server port. Keep `3306` unless it was changed in XAMPP.
- `mysql_user`: MySQL username. XAMPP commonly uses `root`.
- `mysql_password`: Password for the configured MySQL user. XAMPP commonly leaves the root password blank.
- `backup_dir`: Folder where backups should be stored. Replace `E:/EXAMPLE/backups` with a real folder on your system.
- `retention_days`: Number of days to keep backup files.
- `excluded_databases`: Databases that should not be exported. Remove a name from this list if you want it included.

Use forward slashes in paths inside `config.json`, for example:

```json
"backup_dir": "D:/Database Backups"
```

### 2. Configure `manual-backup.bat`

Open `manual-backup.bat` and change this line so it points to the folder where
this project is located:

```bat
cd /d E:\simple-db-backup
```

For example:

```bat
cd /d C:\Users\YourName\Projects\simple-db-backup
```

### 3. Test the configuration

Start MySQL from the XAMPP Control Panel, then double-click
`manual-backup.bat`.

After it finishes, check:

- The configured backup folder contains a folder named with today's date.
- That folder contains one `.sql.gz` export for each included database.
- `logs/backup.log` ends with `Backup completed successfully.`

If the backup fails, check the latest error in `logs/backup.log`.

## Run Manually

Start MySQL in XAMPP, then double-click:

```text
manual-backup.bat
```

You can also run the Python script from the project folder:

```powershell
python backup.py
```

## Set Up Automatic Backups

Open Command Prompt and create a Windows Scheduled Task with:

```cmd
schtasks /Create /TN "MySQL Auto Backup" /TR "python E:\simple-db-backup\backup.py" /SC WEEKLY /D MON,TUE,WED,THU,FRI /ST 18:10
```
*Note: If the command running the script itself fails and/or fails to find it, you can alternatively run the command so it runs the manual-backup.bat executable.*

```cmd
schtasks /Create /TN "MySQL Auto Backup" /TR "\"E:\simple-db-backup\run-backup.bat\"" ^  /SC WEEKLY ^  /D MON,TUE,WED,THU,FRI ^  /ST 18:10 ^
```

Before running the command, replace:

- `E:\simple-db-backup\backup.py` with the full path to your `backup.py`.
- `MON,TUE,WED,THU,FRI` with the days when backups should run.
- `18:10` with the desired start time in 24-hour format.

For a backup every day at 18:10, use:

```cmd
schtasks /Create /TN "MySQL Auto Backup" /TR "python E:\simple-db-backup\backup.py" /SC DAILY /ST 18:10
```

The computer must be on and XAMPP MySQL must be running when the task starts.

