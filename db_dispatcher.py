import sqlite3
from support import generate_code

con = sqlite3.connect("wishlist_db")
cur = con.cursor()


def add_user(username):
    us = cur.execute('SELECT user_name FROM users WHERE user_name = ?', (username, )).fetchall()
    if not us:
        cur.execute('INSERT INTO users(user_name) VALUES(?)', (username, ))
        con.commit()


def add_wishlist(username, listname):
    listcode = generate_code(10)
    userid = cur.execute('SELECT user_id FROM users WHERE user_name = ?', (username, )).fetchone()[0]
    cur.execute('INSERT INTO wishlists(user_id, list_code, list_name) VALUES(?, ?, ?)', (userid, listcode, listname))
    con.commit()
    listid = cur.execute('SELECT list_id FROM wishlists WHERE list_code = ?', (listcode, )).fetchone()[0]
    return listcode, listid

def take_wihslists(username):
    users_lists = cur.execute("""SELECT * FROM wishlists
                                    Where user_id=(
                                SELECT user_id FROM users
                                    WHERE user_name = ?)""", (username,)).fetchall()
    return users_lists

def save_item(listid, iteminfo):
    cur.execute('INSERT INTO items(list_id, item_info) VALUES(?, ?)', (listid, str(iteminfo)))
    con.commit()

def take_all_items(listid):
    us = cur.execute('SELECT item_info FROM items WHERE list_id = ?', (listid, )).fetchall()
    return us

