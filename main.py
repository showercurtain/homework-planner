#!/usr/bin/env python3

# import everything important from storage.py file
import os
exec(open(os.path.join(os.getcwd(),'storage.py')).read())

db = Database('example.db')
db.listhomework(0)
