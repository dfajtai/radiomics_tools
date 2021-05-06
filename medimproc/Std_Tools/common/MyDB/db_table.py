#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os,sys, errno
from optparse import OptionParser
import sqlite3
import pandas as pd
import numpy as np
import time

# import unidecode

sys.path.insert(0, '/home/fajtai/py/')

from Common.MyCsv import *
from Common.colorPrint import *
from Std_Tools.common.unidecode import unidecode, strcode


def clean_text(row):
    # return the list of decoded cell in the Series instead
    return [r.decode('unicode_escape').encode('ascii', 'ignore') for r in row]

def check_connection(func):
    def inner_func(self,*args,**kwargs):
        # print(func)
        fail_count = 0
        success = False
        r = None

        while fail_count < 4 and success == False:
            try:
                r =  func(self, *args, **kwargs)
                success = True

            except sqlite3.OperationalError:
                printWarning("database error in {0}".format(str(func)))
                if fail_count > 0:
                    printInfo(
                        "{0}th attempt to connect database {1}".format(str(fail_count + 1), str(self.db_path)))
                time.sleep(2)
                fail_count += 1
        if success:
            return r

    return inner_func


def temporal_connection(func):
    def inner_func(self,*args,**kwargs):
        # print(func)
        fail_count = 0
        success = False
        r = None

        while fail_count < 4 and success == False:
            try:
                db = DB_Connector.add_DB_connection(self.db_path)
                self.conn = db.conn
                self.c = db.c

                r =  func(self, *args, **kwargs)
                db.disconnect()
                success = True

            except sqlite3.OperationalError:
                printWarning("database error in {0}".format(str(func)))
                if fail_count > 0:
                    printInfo(
                        "{0}th attempt to connect database {1}".format(str(fail_count + 1), str(self.db_path)))
                time.sleep(2)
                fail_count += 1
        if success:
            return r

    return inner_func


class DB(object):
    print_connection = False
    def __init__(self,db_path):
        if not os.path.exists(db_path):
            printWarning("Error! Database '{0}' not exists!".format(db_path))
            if db_path=="":
                printError("Error! Database '{0}' can not be created!".format(db_path))
                raise IOError
            printInfo("Create database '{0}'...".format(db_path))

        self.db_path = strcode(db_path)

        self.connected = False
        self.conn, self.cursor = None, None

    def connect(self):
        fail_count = 0
        conn, cursor = None, None

        if self.connected:
            return

        while fail_count < 5 and self.connected == False:
            try:
                if fail_count > 0:
                    printInfo("{0}th attempt to connect database {1}".format(str(fail_count + 1), str(self.db_path)))
                conn = sqlite3.connect(strcode(self.db_path))
                cursor = conn.cursor()
                self.connected = True
                if DB.print_connection:
                    printInfo("Connected to database '{0}'".format(self.db_path))
            except sqlite3.OperationalError as e:
                time.sleep(0.5)
                fail_count -= 1

        if self.connected:
            self.conn = conn
            self.c = cursor


    def disconnect(self):
        if DB.print_connection:
            printInfo("Disconnected form '{0}'".format(self.db_path))
        self.conn.close()
        self.connected = False

    def __del__(self):
        if DB.print_connection:
            printInfo("Disconnected form database '{0}'".format(self.db_path))
        self.conn.close()
        self.connected = False


class DB_Connector(object):
    db_s = {}
    @staticmethod
    def add_DB_connection(db_path):
        if db_path not in DB_Connector.db_s.keys():
            db = DB(db_path)
            db.connect()
            DB_Connector.db_s[db_path]=db
            return db

        else:
            if isinstance(DB_Connector.db_s[db_path],DB):
                if not DB_Connector.db_s[db_path].connected:
                    DB_Connector.db_s[db_path].connect()
                return DB_Connector.db_s[db_path]


class DB_Table(object):
    def __init__(self,db_path, *connections):
        if not os.path.exists(db_path):
            printWarning("Error! Database '{0}' not exists!".format(db_path))
            if db_path=="":
                printError("Error! Database '{0}' can not be created!".format(db_path))
                raise IOError
            printInfo("Create database '{0}'...".format(db_path))

        self.db_path = db_path

        self.T_NAME = ""
        self.COLS = {}
        self._COLS = []
        self.KEY = []
        self.connections = connections

        db = DB_Connector.add_DB_connection(db_path)
        self.conn = db.conn
        self.c = db.c

    def sync_cols(self,orig_df):
        if not isinstance(orig_df,pd.DataFrame):
            return
        new_cols = pd.DataFrame()
        for c in self._COLS:
            if c not in orig_df.keys():
                new_cols = pd.concat([new_cols,pd.Series([],name=c)], axis=1)

        new_df = pd.concat([orig_df,new_cols],axis=1)[self._COLS]
        return new_df

    @check_connection
    def _foreign_key_text(self, col_in_place, table, col):
        return "FOREIGN KEY ({0}) REFERENCES {1}({2})".format(col_in_place,table,col)

    @check_connection
    def _find_connections(self):
        col1,table,col2 = [],[],[]
        for c in self.connections:
            if issubclass(c.__class__,DB_Table):
                for k in c.KEY:
                    if k in self.KEY:
                        col1.append(k)
                        table.append(c.T_NAME)
                        col2.append(k)
        return zip(col1,table,col2)

    @check_connection
    def Create(self,overwrite=False):
        if not self.table_exists():
            self.create_table()
            self.save_table()
        else:
            if overwrite:
                self.create_table(auto_remove=overwrite)
                self.save_table()
            else:
                self.create_missing_columns()

    @check_connection
    def create_table(self,auto_remove=False):
        if auto_remove:
            self.c.execute("DROP TABLE IF EXISTS {0};".format(self.T_NAME))

        create_command = "CREATE TABLE IF NOT EXISTS {0}".format(self.T_NAME)
        col_texts = ["{col} {data_type}".format(col=k,data_type=str(self.COLS[k]).upper()) for k in self._COLS]
        if self.KEY != []:
            keys = ",".join(self.KEY)
            col_texts.append("PRIMARY KEY ({0})".format(keys))

        connections = self._find_connections()
        foreign_key_text = [self._foreign_key_text(*c[:]) for c in connections]
        col_texts.extend(foreign_key_text)

        create_command += "({});".format(",\n".join(col_texts))
        # print create_command
        self.c.execute(create_command)

    @check_connection
    def create_missing_columns(self):
        if not self.table_exists():
            return None
        existing_cols = self.get_col_names()
        missing = list(set(self._COLS).difference(set(existing_cols)))
        if len(missing)==0:
            return None
        printInfo("Missing column detected in '{0}'. Recreating table...".format(self.T_NAME))
        df = self.sync_cols(self.read_table())
        self.create_table(auto_remove=True)
        self.insert_df(df)
        self.save_table()
        printInfo("Done")

    @check_connection
    def add_record(self,**values):

        cols_ = [k for k in values.keys() if k in self._COLS]
        cols_.sort()
        cols = ["{0}".format(str(c)) for c in cols_]
        k = ",".join(cols)

        # print(values)
        # vals = ["'{0}'".format(str(unidecode(values[c]))) for c in cols_]

        try:
            # if not isinstance(values.get("name"),type(None)):
            # if not values.get("name") == "":
            #     print("name")

            vals = ["'{0}'".format(unidecode(values[c])) for c in cols_]
            # vals = ["'{0}'".format(str(values[c])) for c in cols_]
            v = ",".join(vals)

            add_command = "INSERT OR IGNORE INTO {0}({1}) VALUES ({2})".format(self.T_NAME,k,v)
            # print(add_command)
            self.c.execute(add_command)

        except Exception as e:
            print(str(e))


    @check_connection
    def overwrite_record(self,**values):
        cols_ = [k for k in values.keys() if k in self._COLS]
        cols_.sort()
        cols = ["{0}".format(str(c)) for c in cols_]
        k = ",".join(cols)
        vals = ["'{0}'".format(str(unidecode(values[c]))) for c in cols_]

        # vals = ["'{0}'".format(str(values[c])) for c in cols_]
        v = ",".join(vals)

        add_command = "INSERT OR REPLACE INTO {0}({1}) VALUES ({2})".format(self.T_NAME,k,v)

        self.c.execute(add_command)

    @check_connection
    def update_where(self,values,**conditions):
        if not self.table_exists():
            return None
        cond_valid_columns = np.array([c for c in conditions.keys() if c in self.COLS.keys()])
        cond_key_value = " AND ".join(["{0} = '{1}'".format(k,conditions[k]) for k in cond_valid_columns])

        val_valid_columns = np.array([c for c in values.keys() if c in self.COLS.keys()])
        val_key_value = ", ".join(["{0} = '{1}'".format(k, values[k]) for k in val_valid_columns])

        command = "UPDATE {0} SET {1} WHERE ({2});".format(self.T_NAME,val_key_value,cond_key_value)
        # print command
        self.c.execute(command)

    # @check_connection
    def table_exists(self):
        statement = "SELECT name FROM sqlite_master WHERE type='table';"
        if (self.T_NAME,) in self.c.execute(statement).fetchall():
            return True
        return False

    @check_connection
    def get_col_names(self):
        if not self.table_exists():
            return None
        db_cols = self.c.execute("PRAGMA table_info({0});".format(self.T_NAME)).fetchall()
        db_col_names = [c[1] for c in db_cols]
        return db_col_names

    @check_connection
    def get_cols(self,*cols):
        if not self.table_exists():
            return None
        db_cols = self.c.execute("PRAGMA table_info({0});".format(self.T_NAME)).fetchall()
        db_col_names = [c[1] for c in db_cols]

        filtered_cols = [c for c in cols if c in db_col_names]

        rows = self.c.execute("SELECT {1} FROM {0};".format(self.T_NAME,", ".join(filtered_cols))).fetchall()
        return pd.DataFrame(rows,columns=filtered_cols)

    @check_connection
    def read_key_value_dict(self,key,value):
        if not self.table_exists():
            return None
        rows = self.c.execute("SELECT * FROM {0};".format(self.T_NAME)).fetchall()
        cols = self.c.execute("PRAGMA table_info({0});".format(self.T_NAME)).fetchall()
        col_names = [c[1] for c in cols]

        df = pd.DataFrame(rows,columns=col_names)
        d = {}

        if key in self.KEY and value in self.COLS and key in col_names and value in col_names:
            for idx,row in df.iterrows():
                d[unidecode(row[key])] = unidecode(row[value])

        return d

    @check_connection
    def read_table(self,print_it = False):
        """
        :param print_it:
        :return:
        :rtype: pd.DataFrame
        """
        if not self.table_exists():
            return None

        rows = self.c.execute("SELECT * FROM {0};".format(self.T_NAME)).fetchall()

        cols = self.c.execute("PRAGMA table_info({0});".format(self.T_NAME)).fetchall()
        col_names = [c[1] for c in cols]
        # print col_names

        table_data = pd.DataFrame(rows,columns=col_names)
        table_data=table_data.applymap(lambda x:unidecode(x))
        if print_it: print(table_data)

        return table_data

    @check_connection
    def delete_where(self, **kwargs):
        if not self.table_exists():
            return None
        valid_columns = np.array([c for c in kwargs.keys() if c in self.COLS.keys()])

        key_value = " AND ".join(["{0} = '{1}'".format(k,kwargs[k]) for k in valid_columns])

        command = "DELETE FROM {0} WHERE ({1});".format(self.T_NAME,key_value)

        self.c.execute(command)

    @check_connection
    def get_record_where(self,**kwargs):
        if not self.table_exists():
            return None
        valid_columns = np.array([c for c in kwargs.keys() if c in self.COLS.keys()])

        key_value = " AND ".join(["{0} = '{1}'".format(k,kwargs[k]) for k in valid_columns])

        command = "SELECT * FROM {0} WHERE ({1});".format(self.T_NAME,key_value)

        rows = self.c.execute(command).fetchall()

        cols = self.c.execute("PRAGMA table_info({0});".format(self.T_NAME)).fetchall()
        col_names = [c[1] for c in cols]

        return pd.DataFrame(rows,columns=col_names)

    @check_connection
    def get_record_list(self,*cols):
        records = self.read_table()
        if isinstance(records,pd.DataFrame):
            valid_keys = [c for c in cols if c in records.columns]
            return records[:][np.array(valid_keys)]

    @check_connection
    def insert_df(self, data_frame):
        if not isinstance(data_frame,pd.DataFrame):
            return
        valid_columns = np.array([c for c in data_frame.columns if c in self.COLS.keys()])
        for idx,row in data_frame.iterrows():
            data = row[valid_columns]
            # print(row)
            self.add_record(**data.to_dict())

    def get_dummy_dataframe(self):
        return pd.DataFrame(columns=self._COLS)

    @check_connection
    def save_table(self):
        self.conn.commit()

    @check_connection
    def rename_table(self,new_name):
        command = "ALTER TABLE {0} RENAME TO {1};".format(self.T_NAME, new_name)
        self.T_NAME = new_name
        self.c.execute(command)

    #region CSV
    @check_connection
    def pull_data_from_csv(self, csv_file,save_table = True):
        if not os.path.exists(csv_file):
            return None
        csv_df = pd.read_csv(csv_file,encoding="utf-8")
        # dict_list = MyCsv.readDictList(csv_file)
        # csv_df = pd.DataFrame(dict_list)
        self.insert_df(csv_df)
        if save_table:
            self.save_table()

        return csv_df

    @check_connection
    def save_2_csv(self,csv_file):
        data = self.read_table()
        data.to_csv(csv_file,sep=",",mode="w",index=False,encoding="utf-8")
        printInfo("Saving table '{0}' from database '{1}' to '{2}'".format(self.T_NAME,self.db_path,csv_file))
    #endregion


def main():
    pass

if __name__ == '__main__':
    main()

