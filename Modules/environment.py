#!/usr/bin/env python

import os

def run(**args):
	print "[+] Fetching OS env variables"
	return str(os.environ)

	