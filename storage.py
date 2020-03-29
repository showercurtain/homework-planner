#!/usr/bin/env python3
import sqlite3 as sql
from datetime import date
from datetime import datetime as time
import os, requests, json, datetime

class Database:
    def __init__(self,filename=':memory:',connection=None):
        if connection == None:
            if filename == ':memory:':raise Exception
            self._db = sql.connect(filename)
            self._c = self._db.cursor()
            self.filename = filename
        else:
            self._db = connection
            self._c = self._db.cursor()
            self.filename = filename
    def students(self):
        return self._c.execute("SELECT name, id FROM students").fetchall()
    
    def classes(self,studentid):
        return self._c.execute("SELECT name, id FROM classes WHERE classes.student_id == ?",(studentid,)).fetchall()
    
    def homework(self,classid):
        return self._c.execute("SELECT name, id, duedate, assigned, percent FROM homework WHERE homework.class_id == ?",(classid,)).fetchall()
    
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
            if i[5] == 100:
                continue
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
                    
    def save(self,filename=None):
        if filename == None:
            if self.filename != ':memory:':
                self._db.commit()
        elif self.filename == filename:
            self._db.commit()
        elif filename != ':memory:':
            if os.path.exists(filename):
                os.remove(filename)
            temp = sql.connect(filename)
            c = temp.cursor()
            for i in self._db.iterdump():
                c.execute(i)
            temp.commit()
            self._db.close()
            self._db = temp
            self._c = c
        else:
            raise Exception
        
    def close(self):
        self._db.close()
        
    def save_exit(self):
        self.save()
        self.close()

    def load_veracross(self,username,password,student_id):
        session_requests = requests.Session()

        payload = {
            "username":username,
            "password":password,
            "commit":"Log In",
            "return_to":"https://portals-embed.veracross.com/ahs/student/planner"
            }
        data = requests.Session().post("https://portals-embed.veracross.com/ahs/login", data={"username":"sean.cowley","password":"asdfASDF1","commit":"Log In","return_to":"https://portals-embed.veracross.com/ahs/student/planner"}).text
        data = dict(json.loads(data[data.find("Portals.Family.AssignmentPlanner.App({")+37:data.find("}]\n      });")+10].replace('rows','"rows"').replace('columns','"columns"').replace('items','"items"')))
        classes = {}
        dates = {}
        for i in data['rows']:
            classes.update({i['id']:i['description']})
            
        class item(object):
            def __init__(self,data):
                self.name = data['notes']
                self.assigned = datetime.datetime.strptime(data['date'],"%Y-%m-%dT00:00:00.000Z")
                self.clas = classes[data['row']]
                try:
                    tmp = data['formatted_date'].split(' ')
                    dom = int(tmp[1])
                    month = datetime.datetime.strptime(tmp[0],'%b').month
                    now = datetime.datetime.now()
                    if now.month > 7:
                        if month > 7:
                            year = now.year
                        else:
                            year = now.year + 1
                    else:
                        year = now.year
                except:
                    year = self.assigned.year
                    month = self.assigned.month
                    dom = self.assigned.day
                self.date = datetime.datetime(year,month,dom)
                
        hw = []
        for i in data['items']:
            hw.append(item(i))

        for i in hw:
            if i.clas not in [i[0] for i in self.classes(student_id)]:
                self.addclass(i.clas,student_id)
            if i.date < datetime.datetime.today():
                continue
            classes = self.classes(student_id)
            class_id = [i[1] for i in classes][[i[0] for i in classes].index(i.clas)]
            if i.name not in [i[0] for i in self.homework(class_id)]:
                self.addhomework(i.name,class_id,i.date,i.assigned)

def newdb(filename=':memory:'):
    if filename != ':memory:':
        if os.path.exists(filename):
            os.remove(filename)
    db = sql.connect(filename)
    c = db.cursor()
    c.execute("CREATE TABLE students (id int,name string,grade int)")
    c.execute("CREATE TABLE classes (id int,name string,student_id int)")
    c.execute("CREATE TABLE homework (id int,name string,class_id int,duedate date,assigned date,percent int)")
    db.commit()
    c.close()
    return Database(filename,db)

x = newdb()
x.addstudent("Sean",9)
x.load_veracross("sean.cowley","asdfASDF1",0)
x.listhomework(0)
