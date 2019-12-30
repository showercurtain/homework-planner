#!/usr/bin/env

import sqlite3 as sql
from datetime import date
from datetime import datetime as time
import os

## class used for storing data about homework
class Homework(object):
    def __init__(self, name, duedate):
        self.name = name
        self.due = duedate
        self.assigned = date.today()
        self.completed = 0
    def complete(self,percent=100):
        self.completed = percent
        if self.completed >= 100:
            self.completed = True

## This is the class used to store the user's data
class User(object):
    def __init__(self, name, grade):
        self.name = name
        self.grade = grade
        self.classes = {}

    def addclass(self, name):
        self.classes.update({name:[]})

    def getclass(self,classno):
        if type(classno) == int:
            key = list(self.classes.keys())[classno]
        elif type(classno) == str:
            key = classno
        else:
            key = None
        return key

    def addhomework(self, classno, name, duedate):
        key = self.getclass(classno)
        if key:
            self.classes[key].append(Homework(name,duedate))
        
    def completehomework(self, classno, homeworkno, percent=100):
        key = self.getclass(classno)
        if not key:
            return None
        if type(homeworkno) == int:
            hw = homeworkno
        elif type(homeworkno) == str:
            for i in range(len(self.classes[key])):
                if self.classes[key][i].name == homeworkno:
                    hw = i
                    break
            if not hw:
                return None
        else:
            return None
        self.classes[key][hw].complete(percent)
        if self.classes[key][hw].completed == True:
            del self.classes[key][hw]
            
    def removeclass(self,classno):
        key = self.getclass(classno)
        del self.classes[key]

    def listhomework(self):
        for i in self.classes.keys():
            print("Homework for",i+":")
            for j in self.classes[i]:
                print("    ",end='')
                print(j.name+", Due "+j.due.strftime("%B %m, %Y"))

def data_out(filename,data):
    if os.path.exists(filename):
        os.remove(filename)
    db = sql.connect(filename)
    c = db.cursor()
    c.execute("CREATE TABLE students (myid int,stname string,grade int)")
    c.execute("CREATE TABLE classes  (theid int,clname string,stid int)")
    c.execute("CREATE TABLE homework (       hwname string,clid int,duedate string,date string,percent int)")
    classno = 0
    for i in range(len(data)):
        c.execute("INSERT INTO students VALUES (?,?,?)",(i,data[i].name,data[i].grade))
        for j in data[i].classes.keys():
            c.execute("INSERT INTO classes VALUES (?,?,?)",(classno,j,i))
            for k in data[i].classes[j]:
                c.execute("INSERT INTO homework VALUES (?,?,?,?,?)",(k.name,classno,k.due.strftime("%D"),k.assigned.strftime("%D"),k.completed))
            classno += 1
    db.commit()
    db.close()
def data_in(filename):
    db = sql.connect(filename)
    c = db.cursor()
    data = []
    name = 0
    clas = 0
    user = -1
    rawdata = c.execute("SELECT stname,grade,clname,hwname,duedate,date,percent FROM homework JOIN classes ON homework.clid = classes.theid JOIN students ON students.myid = classes.stid").fetchall()
    for i in rawdata:
        if name != i[0]:
            data.append(User(i[0],i[1]))
            name = i[0]
            user += 1
        if clas != i[2]:
            data[user].addclass(i[2])
            clas = i[2]
        data[user].addhomework(clas,i[3],time.strptime(i[4],"%m/%d/%y"))
        data[user].classes[clas][len(data[user].classes[clas])-1].assigned = time.strptime(i[5],"%m/%d/%y")
        data[user].classes[clas][len(data[user].classes[clas])-1].completed = i[6]
    return data
