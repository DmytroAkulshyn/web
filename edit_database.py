import sqlite3
from werkzeug.security import generate_password_hash
connection = sqlite3.connect('sqlite.db', check_same_thread=False)
cursor = connection.cursor()

cursor.execute(
    '''
                    CREATE TABLE user (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL
                    );
                    ''')
cursor.execute('ALTER TABLE post ADD author_id INTEGER;')

cursor.execute('ALTER TABLE user TABLE ADD COLUMN email TEXT UNIQUE;')

cursor.execute('UPDATE user SET email = "example@gmail.com WHERE" id = 1;')

cursor.execute('INSERT INTO user VALUES (?, ?, ?) ',
               (1, 'Rocket', generate_password_hash('qwerty'), 'email@gmail.com'))
cursor.execute('UPDATE post SET author_id = 1;')

result = cursor.execute(
        'SELECT * FROM user'
    ).fetchone()
print(result)

connection.commit()
connection.close()