#!/usr/bin/env python

import os

def run(**args):
	print "[+] Inside Dirlister"
	files =  os.listdir(".")
	return str(files)