#!/usr/bin/env

import sqlite3 as sql
from datetime import date

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

showercurtain = User("My Name",10)

showercurtain.addclass("Fezziks")
showercurtain.addclass("Book Reading Period")
showercurtain.addclass("Evil Numbers Class")

showercurtain.addhomework("Fezziks","Two's Day",date(2022,2,22))
showercurtain.addhomework(0,"Cold Fusion",date(1989,3,25))
showercurtain.addhomework("Fezziks","Program",date(2019,12,27))
showercurtain.addhomework(2,"Problem Set 14159265",date(2020,3,14))
showercurtain.addhomework(1,"Read \"A Brief History of Time\", by Stephen Hawking",date(2018,11,16))
showercurtain.addhomework("Book Reading Period","Finish writing short, 573 page composition about books",date(2019,12,26))

showercurtain.completehomework(0,"Two's Day",98)
showercurtain.completehomework(0,2,19)
showercurtain.completehomework("Fezziks",1,2)
showercurtain.completehomework(2,0,99)
showercurtain.completehomework(1,1,2)
showercurtain.completehomework(1,0)

showercurtain.listhomework()
