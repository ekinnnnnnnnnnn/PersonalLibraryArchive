import sqlite3

conn=sqlite3.connect("Lib.db")
c=conn.cursor()

c.execute('''create table if not exists user(
          id integer primary key autoincrement,
          username text not null unique,
          pw text not null,
          salt text not null)''')

c.execute('''create table if not exists books(
          id integer primary key autoincrement,
          userid integer not null,
          bookname text not null,
          author text not null,
          status text default 'not read yet',
          foreign key (userid) references user(id))''')

c.execute('''create table if not exists comments(
          id integer primary key autoincrement,
          bookid integer not null,
          userid integer not null,
          comment text,
          date timestamp default current_timestamp,
          foreign key (bookid) references books(id),
          foreign key (userid) references user(id))''')

conn.commit()
conn.close()