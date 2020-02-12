#!/usr/bin/env python3
import sqlite3 as sql
from datetime import date
from datetime import datetime as time
import os

class Database:
    def __init__(self,filename):
        self._db = sql.connect(filename)
        self._c = self._db.cursor()
        
    def students(self):
        return self._c.execute("SELECT name, id FROM students").fetchall()
    
    def classes(self,studentid):
        return self._c.execute("SELECT name, id FROM classes WHERE classes.student_id == ?",(studentid,)).fetchall()
    
    def homework(self,classid):
        return self._c.execute("SELECT name, hw_id, duedate, assigned, percent, FROM homework WHERE homework.class_id == ?",(classid,)).fetchall()
    
    def addstudent(self,name,grade):
        id = self._c.execute("SELECT COUNT(*) FROM students").fetchall()[0][0]
        self._c.execute("INSERT INTO students VALUES (?,?,?)",(id,name,grade))
        
    def addclass(self,name,studentid):
        id = self._c.execute("SELECT COUNT(*) FROM classes").fetchall()[0][0]
        self._c.execute("INSERT INTO classes VALUES (?,?,?)",(id,name,studentid))
        
    def addhomework(self,name,classid,duedate,assigned='today'):
        if assigned=='today':assigned=time.now()
        id = self._c.execute("SELECT COUNT(*) FROM homework").fetchall()[0][0]
        self._c.execute("INSERT INTO homework VALUES (?,?,?,?,?,?)",
                       (id,name,classid,duedate.strftime("%Y-%m-%d"),assigned.strftime("%Y-%m-%d"),0))
        
    def completehomework(self,homeworkid,percent=100):
        if percent==100:
            self._c.execute("DELETE FROM homework WHERE homework.id == ?",(homeworkid,))
        else:
            self._c.execute("UPDATE homework SET percent = ? WHERE homework.id == ?",(percent,homeworkid))
            
    def removeclass(self,classid):
        self._c.execute("DELETE FROM homework WHERE homework.class_id == ?",(classid,))
        self._c.execute("DELETE FROM classes WHERE classes.id == ?",(classid,))
        
    def removestudent(self,studentid):
        data = self._c.execute("SELECT class_id FROM classes WHERE student_id == ?",(studentid,)).fetchall()
        for i in data:
            self.removeclass(i[0])
        self._c.execute("DELETE FROM students WHERE id == ?",(studentid,))

    def _listhomework(self,studentid):
        data = self._c.execute("""SELECT students.name,classes.name,homework.name,homework.duedate,homework.assigned,homework.percent FROM students
                                 JOIN classes ON students.id = classes.student_id
                                 JOIN homework ON classes.id = homework.class_id
                                 WHERE students.id = ?""",(studentid,)).fetchall()
        if data == []:return None
        studentname = data[0][0]
        print(studentname+"'s Homework:")
        classname = ''
        for i in data:
            if classname != i[1]:
                print("    Homework for",i[1])
                classname = i[1]
            duedate = date(int(i[3].split('-')[0]),int(i[3].split('-')[1]),int(i[3].split('-')[2]))
            assigned = date(int(i[4].split('-')[0]),int(i[4].split('-')[1]),int(i[4].split('-')[2]))
            print("       ",i[2]+', due',duedate.strftime('%B %d, %Y')+', assigned',assigned.strftime("%B %d, %Y")+',',str(i[5])+'% completed')

    def listhomework(self,studentid):
        if type(studentid) in [list,tuple]:
            [self._listhomework(i) for i in studentid]
        else:
            self._listhomework(studentid)
                    
    def save(self):
        self._db.commit()
        
    def close(self):
        self._db.close()
        
    def save_exit(self):
        self.save()
        self.close()
        
    def _raw(self,studentid):
        data = self._c.execute("""SELECT students.name,classes.name,homework.name,homework.duedate,homework.assigned,homework.percent FROM students
                                 JOIN classes ON students.id = classes.student_id
                                 JOIN homework ON classes.id = homework.class_id
                                 WHERE students.id = ?""",(studentid,)).fetchall()
        if data == []:return None
        studentname = data[0][0]
        classname = ''
        rawdata = {}
        for i in data:
            if classname != i[1]:
                classname = i[1]
                rawdata[studentname].update({classname:[]})
            duedate = date(int(i[3].split('-')[0]),int(i[3].split('-')[1]),int(i[3].split('-')[2]))
            assigned = date(int(i[4].split('-')[0]),int(i[4].split('-')[1]),int(i[4].split('-')[2]))
            rawdata[studentname][classname].append([i[2],duedate.strftime('%B %d, %Y'),assigned.strftime("%B %d, %Y"),i[5]])
        return rawdata
    
    def raw(self,studentid):
        if type(studentid) in [list,tuple]:
            return [self._raw(i) for i in studentid]
        else:
            return self._raw(studentid)

def newdb(filename):
    if os.path.exists(filename):
        os.remove(filename)
    db = sql.connect(filename)
    c = db.cursor()
    c.execute("CREATE TABLE students (id int,name string,grade int)")
    c.execute("CREATE TABLE classes (id int,name string,student_id int)")
    c.execute("CREATE TABLE homework (id int,name string,class_id int,duedate date,assigned date,percent int)")
    db.commit()
    db.close()
    return Database(filename)
