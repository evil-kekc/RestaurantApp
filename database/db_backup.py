import shutil

from database.models import *

if not os.path.exists(fr'{BASE_DIR}/database/backup_files'):
    os.makedirs(fr'{BASE_DIR}/database/backup_files')


def create_backup():
    database_file = fr'{BASE_DIR}/database/db_files/bot_db.db'
    backup_file = fr'{BASE_DIR}/database/backup_files/bot_db.db'

    shutil.copyfile(database_file, backup_file)


if __name__ == '__main__':
    create_backup()
