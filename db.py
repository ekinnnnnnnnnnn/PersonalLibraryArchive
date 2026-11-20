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
          type text not null,
          status text not null default 'not read',
          rating integer not null default 0,
          tPage integer not null,
          rPage integer not null default 0,
          pdfF text not null default 'not uploaded',
          imageF text not null default 'not uploaded',
          foreign key (userid) references user(id) on delete cascade)''')

c.execute('''create table if not exists comments(
          id integer primary key autoincrement,
          bookid integer not null,
          userid integer not null,
          comment text not null,
          date timestamp default current_timestamp not null,
          foreign key (bookid) references books(id) on delete cascade,
          foreign key (userid) references user(id) on delete cascade)''')

conn.commit()
conn.close()