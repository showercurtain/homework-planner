#!/usr/bin/env python3

# import everything important from storage.py file
import os
from storage import Database

db = Database('example.db')
db.listhomework(0)
