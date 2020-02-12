#!/usr/bin/env python3

# import everything important from storage.py file
import os
from datetime import date
from storage import Database
from storage import newdb

db = Database("example.db")

db.listhomework([0,1])
