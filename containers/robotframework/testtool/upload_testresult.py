#!/usr/bin/python3

import os
import sys
import requests

# e.g. /upload_testresult.py "./../" "http://127.0.0.1:8080" "21347283742893742389" "example1"
def get_usage():
    return """
upload_testcase_result.py  <UPLOAD_FOLDER> [<TESTRESULT_SERVER_ADDRESS>] [<TESTRUN_NAMESPACE>] [<TESTCASE>]
   
   Uploads a testresult of an testcase to the testresult server
   
Arguments:
   <UPLOAD_FOLDER>                 ... Local folder where the testcase is included
   <TESTRESULT_SERVER_ADDRESS>     ... Target Addresse to testresult server
   <TESTRUN_NAMESPACE>             ... Namespace of the testrun (=timestamp)
   <TESTCASE>                      ... Name of testcase
"""

# this function is called iterative for all subfolders to upload 
def upload_testresult_folder(upload_folder, testresult_server_address="http://svc-testresultserver.testresultserver", 
                              testrun_namespace=os.environ['NAMESPACE'], testcase=os.environ['TESTCASE']):
   upload_files_dict = {}
   for file in os.listdir(upload_folder):
      full_file_path = os.path.join(upload_folder, file)
      if os.path.isdir(full_file_path):
         upload_testresult_folder(upload_folder=full_file_path,
                        testresult_server_address=testresult_server_address, 
                        testrun_namespace=testrun_namespace,
                        testcase=os.path.join(testcase,file))
      else:
         print(full_file_path)
         upload_files_dict[file] = open(full_file_path, 'rb')

   if len(upload_files_dict.keys())==0:
      print("Skip empty folder: " + upload_folder)
      return
   url = testresult_server_address + "/testruns/" + testrun_namespace + "/" + testcase

   r = requests.post(url = url, files=upload_files_dict)
   if r:
      print(str(r.status_code) + ": Upload sucessfully (" + upload_folder + ")")
   else:
      print(str(r.status_code) + ": Upload failed  (" + upload_folder + ")")
      exit(-2)

if __name__ == '__main__':
    if len(sys.argv) != 5:
        print("Error - Invalid Number of arguments")
        print(get_usage())
        exit(-1)

    upload_testresult_folder(parent_folder = sys.argv[1], testresult_server_address = sys.argv[2], 
                           testrun_namespace = sys.argv[3], testcase = sys.argv[4])
    exit(0)
