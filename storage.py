#!/usr/bin/env python3

import sqlite3 as sql
from datetime import date
from datetime import datetime as time
import os

class Database:
    def __init__(self,filename):
        self.db = sql.connect(filename)
        self.c = self.db.cursor()
    def addstudent(self,name,grade):
        my_id = self.c.execute("SELECT COUNT(*) FROM students").fetchall()[0][0]
        self.c.execute("INSERT INTO students VALUES (?,?,?)",(my_id,name,grade))
    def addclass(self,name,studentid):
        the_id = self.c.execute("SELECT COUNT(*) FROM classes").fetchall()[0][0]
        self.c.execute("INSERT INTO classes VALUES (?,?,?)",(the_id,name,studentid))
    def addhomework(self,name,classid,duedate):
        an_id = self.c.execute("SELECT COUNT(*) FROM classes").fetchall()[0][0]
        self.c.execute("INSERT INTO homework VALUES (?,?,?,?,?,?)",
                       (name,classid,duedate.strftime("%Y-%m-%d"),time.now().strftime("%Y-%m-%d"),0,an_id))
    def completehomework(self,homeworkid,percent=100):
        if percent==100:
            self.c.execute("DELETE FROM homework WHERE homework.an_id == ?",(homeworkid,))
        else:
            self.c.execute("UPDATE homework SET percent = ? WHERE homework.an_id == ?",(percent,homeworkid))
    def removeclass(self,classid):
        self.c.execute("DELETE FROM homework WHERE homework.cl_id == ?",(classid,))
        self.c.execute("DELETE FROM classes WHERE classes.the_id == ?",(classid,))
    def removestudent(self,studentid):
        data = self.c.execute("SELECT the_id FROM classes WHERE st_id == ?",(studentid,)).fetchall()
        for i in data:
            self.removeclass(i[0])
        self.c.execute("DELETE FROM students WHERE my_id == ?",(studentid,))
    def listhomework(self,studentid):
        data = self.c.execute("""SELECT * FROM students 
                                 JOIN classes ON students.student_id = classes.student_id
                                 JOIN homework ON classes.class_id = homework.class_id""").fetchall()
        data = [(i[1],i[4],i[6],i[8],i[9],i[10]) for i in data]
        print(data)
    def save(self):
        self.db.commit()
    def close(self):
        self.db.close()
def newdb(filename):
    if os.path.exists(filename):
        os.remove(filename)
    db = sql.connect(filename)
    c = db.cursor()
    c.execute("CREATE TABLE students (student_id int,name string,grade int)")
    c.execute("CREATE TABLE classes (class_id int,name string,student_id int)")
    c.execute("CREATE TABLE homework (name string,class_id int,duedate date,assigned date,percent int,hw_id int)")
    db.commit()
    db.close()
    return Database(filename)

db = Database('example.db')
db.listhomework(0)
