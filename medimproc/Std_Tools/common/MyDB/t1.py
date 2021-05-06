#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from threading import Thread
import time


sys.path.insert(0, '/home/fajtai/py/')
from Std_Tools.common.MyDB import DB_Table


db_path = "/home/fajtai/py/Common/MyDB/test_db.db"
db = DB_Table(db_path)

db.T_NAME = "test"
db.COLS = {"asd": "int",
           "qwe": "text"}
db._COLS = ["asd", "qwe"]
db.KEY = ["asd"]
db.Create(overwrite=True)
db.add_record(asd=1,qwe="qwe")
db.save_table()
# db.conn.close()
db_path = "/home/fajtai/py/Common/MyDB/test_db.db"
db2 = DB_Table(db_path)

db2.T_NAME = "test"
db2.COLS = {"asd": "int",
            "qwe": "text"}
db2._COLS = ["asd", "qwe"]
db2.KEY = ["asd"]
db2.add_record(asd=3,qwe="qwerty")
db2.save_table()

db2.read_table(print_it=True)

db.read_table(print_it=True)

class worker(Thread):
    def run(self):
        for index in range(0,10):
            print("db1 connection {0}".format(str(index)))

            db_path = "/home/fajtai/py/Common/MyDB/test_db.db"
            db = DB_Table(db_path)

            db.T_NAME = "test"
            db.COLS = {"asd": "int",
                       "qwe": "text"}
            db._COLS = ["asd", "qwe"]
            db.KEY = ["asd"]

            db_path = "/home/fajtai/py/Common/MyDB/test_db.db"
            db2 = DB_Table(db_path)

            db2.T_NAME = "test"
            db2.COLS = {"asd": "int",
                        "qwe": "text"}
            db2._COLS = ["asd", "qwe"]
            db2.KEY = ["asd"]

            db2.Create()

            db.Create()
            time.sleep(0.5)
            db.read_table()

class waiter(Thread):
    def run(self):
        for index in range(0, 10):
            print("db2 connection {0}".format(str(index)))
            db_path = "/home/fajtai/py/Common/MyDB/test_db.db"
            db2 = DB_Table(db_path)

            db2.T_NAME = "test"
            db2.COLS = {"asd": "int",
                        "qwe": "text"}
            db2._COLS = ["asd", "qwe"]
            db2.KEY = ["asd"]

            db2.Create()
            # time.sleep(0.52)
            db2.read_table()

# def run():
#     worker().start()
#     waiter().start()
#
# run()



