import sqlite3
import shutil

def merge(filename="messages.db"):
  shutil.copy("messages-0.db",filename)
  con3 = sqlite3.connect(filename)

  con3.execute("ATTACH 'messages-1.db' as dbb")
  con3.execute("ATTACH 'messages-2.db' as dbc")

  con3.execute("BEGIN")
  for row in con3.execute("SELECT * FROM dbb.sqlite_master WHERE type='table'"):
    try:
      combine = "INSERT INTO "+ row[1] + " SELECT * FROM dbb." + row[1]
      con3.execute(combine)
    except sqlite3.IntegrityError as ex:
      exx=ex
      ex=exx
  con3.commit()
  con3.execute("detach database dbb")
  con3.execute("BEGIN")
  for row in con3.execute("SELECT * FROM dbc.sqlite_master WHERE type='table'"):
    try:
      combine = "INSERT INTO "+ row[1] + " SELECT * FROM dbc." + row[1]
      con3.execute(combine)
    except sqlite3.IntegrityError as ex:
      exx=ex
  con3.commit()
  con3.execute("detach database dbc")
  del con3
