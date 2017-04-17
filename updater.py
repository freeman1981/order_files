#!/usr/bin/env python3
import magic
import sqlite3
import os
from common import md5

if __name__ == '__main__':
    conn = sqlite3.connect('files2.db')
    cursor = conn.cursor()
    cursor.execute('''
    SELECT path_ FROM files
    ''')

    for row in cursor.fetchall():
        absolute_path = row[0]
        if not os.path.exists(absolute_path):
            cursor.execute('''
            DELETE FROM files WHERE path_=?
            ''', (absolute_path,))
        else:
            type_ = magic.from_file(absolute_path, mime=True)
            md5_ = md5(absolute_path)
            size = os.path.getsize(absolute_path)
            cursor.execute('''
                        SELECT * FROM files WHERE path_=? AND (type_!=? OR md5!=? OR size!=?)
                        ''', (absolute_path, type_, md5_, size))
            fetched = cursor.fetchone()
            if fetched:
                cursor.execute('''
                            UPDATE files SET type_=?, md5=?, size=?
                            WHERE path_=?
                            ''', (type_, md5_, size, absolute_path))
        conn.commit()
