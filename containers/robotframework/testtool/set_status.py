#!/usr/bin/python3

import os
import sys
import requests
import time
import json

# e.g. /set_status.py "QUEUED" "http://127.0.0.1:8080" "21347283742893742389" "example1"
def get_usage():
    return """
set_status.py <STATUS> [<TESTRESULT_SERVER_ADDRESS>] [<TESTRUN_NAMESPACE>] [<TESTCASE_NAME>]
   
   Set the current status for a testcase in a testrun
   
Arguments:
   <STATUS>                        ... Status for current testcase (QUEUED, RUNNING, FAILED, DONE)
   <TESTRESULT_SERVER_ADDRESS>     ... Target Addresse to testresult server
   <TESTRUN_NAMESPACE>             ... Namespace of the testrun (=timestamp)
   <TESTCASE>                      ... Name of testcase
"""

def set_status(status, testresult_server_address="http://svc-testresultserver.testresultserver", testrun_namespace=os.environ['NAMESPACE'], 
                  testcase=os.environ['TESTCASE']):
   upload_files_dict = {}
   url = testresult_server_address + "/status/" + testrun_namespace + "/" + testcase
   data = {'status': status, 'timestamp': time.time()}
   
   r = requests.post(url = url, data = json.dumps(data))
   if r:
      print(str(r.status_code) + ": Set status sucessfully (" + status + ")")

   else:
      print(str(r.status_code) + ": Set status failed  (" + status + ")")
      exit(-2)

if __name__ == '__main__':
    if len(sys.argv) != 5:
        print("Error - Invalid Number of arguments")
        print(get_usage())
        exit(-1)

    set_status(status = sys.argv[1], testresult_server_address = sys.argv[2], testrun_namespace = sys.argv[3], 
               testcase = sys.argv[4])
    exit(0)
