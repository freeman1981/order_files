#!/usr/bin/env python3
import magic
import sqlite3
import os
from common import md5


PATH = '/home/freeman'
EXCLUDE_DIR_NAMES = ('venvs', 'venv', 'PyCharm', 'env')
EXCLUDE_FULL_PATHS = ('/home/freeman/data/foo',)
EXCLUDE_START_WITH_DIR = '.'


def process_files(root, files, cursor, connection):
    for file in files:
        if file.startswith('.'):
            continue
        path_ = os.path.join(root, file)
        try:
            type_ = magic.from_file(path_, mime=True)
        except PermissionError:
            type_ = None
        try:
            md5_ = md5(path_)
        except PermissionError:
            md5_ = None
        size = os.path.getsize(path_)
        cursor.execute('''
        SELECT EXISTS(SELECT * FROM files WHERE path_=?);
        ''', (path_,))
        fetched = cursor.fetchone()
        if fetched == (1, ):
            cursor.execute('''
            SELECT * FROM files WHERE path_=? AND (type_!=? OR md5!=? OR size!=?)
            ''', (path_, type_, md5_, size))
            fetched = cursor.fetchone()
            if fetched:
                cursor.execute('''
                UPDATE files SET (type_=?, md5_=?, size=?)
                WHERE path_=?
                ''', (type_, md5_, size, path_))
                print('UPDATE PATH={}'.format(path_))
            else:
                print('SKIP PATH={}'.format(path_))
        else:
            cursor.execute('''
            INSERT INTO files (path_, type_, md5, "size") VALUES (?, ?, ?, ?)
            ''', (path_, type_, md5_, size))
            print('INSERT PATH={}'.format(path_))
        connection.commit()


def process_dir(path, cursor, connection):
    for root, dirs, files in os.walk(path, topdown=True):
        dirs[:] = [item for item in list(dirs) if (not item.startswith(EXCLUDE_START_WITH_DIR) and
                                                   item not in EXCLUDE_DIR_NAMES and
                                                   os.path.join(root, item) not in EXCLUDE_FULL_PATHS)]
        process_files(root, files, cursor, connection)

if __name__ == '__main__':
    conn = sqlite3.connect('files.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS files
    (path_ text, type_ text, md5 text, size text, action text, destination text, helper text)
    ''')
    conn.commit()
    try:
        process_dir(PATH, cursor, conn)
    except KeyboardInterrupt:
        print('KeyboardInterrupt')
    finally:
        conn.close()
