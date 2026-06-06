import json
import gzip
import shutil
import subprocess
import logging
from pathlib import Path
from datetime import datetime, timedelta


BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config.json"
LOG_DIR = BASE_DIR / "logs"


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def setup_logger():
    LOG_DIR.mkdir(exist_ok=True)

    log_file = LOG_DIR / "backup.log"

    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )


def mysql_command(config, executable):
    exe_path = Path(config["mysql_bin_dir"]) / executable

    command = [
        str(exe_path),
        f"--host={config['mysql_host']}",
        f"--port={config['mysql_port']}",
        f"--user={config['mysql_user']}"
    ]

    if config["mysql_password"] != "":
        command.append(f"--password={config['mysql_password']}")

    return command


def get_databases(config):
    command = mysql_command(config, "mysql.exe")
    command += [
        "--batch",
        "--skip-column-names",
        "-e",
        "SHOW DATABASES;"
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True
    )

    excluded = set(config["excluded_databases"])

    databases = [
        db.strip()
        for db in result.stdout.splitlines()
        if db.strip() and db.strip() not in excluded
    ]

    return databases


def dump_database(config, database, output_dir):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    sql_file = output_dir / f"{database}_{timestamp}.sql"
    gz_file = output_dir / f"{database}_{timestamp}.sql.gz"

    command = mysql_command(config, "mysqldump.exe")
    command += [
        "--single-transaction",
        "--routines",
        "--triggers",
        "--events",
        database
    ]

    logging.info(f"Backing up database: {database}")

    with open(sql_file, "w", encoding="utf-8") as file:
        subprocess.run(
            command,
            stdout=file,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )

    with open(sql_file, "rb") as source:
        with gzip.open(gz_file, "wb") as target:
            shutil.copyfileobj(source, target)

    sql_file.unlink()

    logging.info(f"Created backup: {gz_file}")


def clean_old_backups(config):
    backup_dir = Path(config["backup_dir"])
    retention_days = int(config["retention_days"])
    cutoff_date = datetime.now() - timedelta(days=retention_days)

    for file in backup_dir.rglob("*.sql.gz"):
        modified_time = datetime.fromtimestamp(file.stat().st_mtime)

        if modified_time < cutoff_date:
            logging.info(f"Deleting old backup: {file}")
            file.unlink()


def run_backup():
    setup_logger()

    try:
        config = load_config()

        backup_dir = Path(config["backup_dir"])
        today_dir = backup_dir / datetime.now().strftime("%Y-%m-%d")
        today_dir.mkdir(parents=True, exist_ok=True)

        databases = get_databases(config)

        if not databases:
            logging.warning("No databases found to back up.")
            return

        logging.info(f"Found databases: {', '.join(databases)}")

        for database in databases:
            dump_database(config, database, today_dir)

        clean_old_backups(config)

        logging.info("Backup completed successfully.")

    except Exception as error:
        logging.exception(f"Backup failed: {error}")
        raise


if __name__ == "__main__":
    run_backup()