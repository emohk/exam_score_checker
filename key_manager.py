import sqlite3
import re

#creates table in db for an exam
def create_key_table(name):
    with sqlite3.connect('checker.db') as con:
        cur = con.cursor()
        command = f'CREATE TABLE {name} (qid TEXT, ans TEXT)'
        cur.execute(command)

#deletes the entire key of an exam from db
def delete_table(name):
    with sqlite3.connect('checker.db') as con:
        cur = con.cursor()
        command = f'DROP TABLE IF EXISTS {name}'
        cur.execute(command)

# TODO
def edit_table(name):
    with sqlite3.connect('checker.db') as con:
        cur = con.cursor()
        cur.execute(f"SELECT * FROM {name};")
        rows = cur.fetchall()
        text = ''
        for row in rows:
            text += f"{row['qid']} {row['ans']}"

# converts text to db
def txt_to_db(text, exam):
    if not text or not exam:
        print('text or exam not provided')
        return
    
    with sqlite3.connect('checker.db') as con:
        cur = con.cursor()
        command = f'INSERT INTO {exam} (qid, ans) VALUES (?, ?)'
        for line in text.split('\n'):
            ids = re.findall(r'\w+', line)
            cur.execute(command, (ids[0], ids[1],))

# checks if the chosen answer is correct from key
def is_right_ans(qid, ansid, table):
    with sqlite3.connect('checker.db') as con:
        cur = con.cursor()
        command = f'SELECT ans FROM {table} WHERE qid = {qid}'
        cur.execute(command)
        rightans = cur.fetchall()[0][0]

    if ansid == rightans or rightans == 'Drop'.casefold or rightans == 'bonus'.casefold:
        return True
    else:
        return False

# returns the name of all exams in key db
def get_table_info():
    with sqlite3.connect('checker.db') as con:
        cur = con.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name != 'mods';")
        tables = cur.fetchall()
        table_info = []
        for table in tables:
            cur.execute(f"SELECT COUNT(*) FROM {table[0]};")
            row_count = cur.fetchone()[0]
            table_info.append({'name': table[0], 'count': row_count})
    return table_info

