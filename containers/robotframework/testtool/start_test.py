#!/usr/bin/python3

import os
from sys import exit
from robot import run_cli
import set_status
import upload_testresult

error=False

testcase = os.environ['TESTCASE']

set_status.set_status("RUNNING")

print("Hello start")

testcase_directory = os.path.join("/", "test")

ret = run_cli(["--reporttitle", testcase, "--outputdir", "/testresult", "--pythonpath", "/testlib", testcase_directory], exit=False)

upload_testresult.upload_testresult_folder("/testresult")

if ret != 0:
   print("Testcase " + testcase + " failed with " + str(ret))
   set_status.set_status("FAILED")
else:
   set_status.set_status("DONE")

#Init process of Container returns 0 even if an error occours in the testcases 
exit(0)