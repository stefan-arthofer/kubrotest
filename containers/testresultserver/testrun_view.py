#!/usr/bin/python3

import os
import sys
import json
import time


### Returns last status for target testcase
def get_testcase_status(testcase_path):
   testcase_status={}
   testcase_status_file = os.path.join(testcase_path, "status.txt")
   if os.path.exists(testcase_status_file):
       f = open(testcase_status_file,"r")
       testcase_status_list = json.loads(f.read())
       f.close()
       testcase_status = testcase_status_list[-1]
   else:
       testcase_status = {'status': 'UNKNOWN', 'timestamp': 0} 
   return testcase_status

def format_status_string(status):
    status_string = ""
    if status == "QUEUED":
        status_string = status_string + '<span class="badge bg-info text-dark">'
    if status == "RUNNING":
        status_string = status_string + '<span class="badge bg-info text-dark">'
    elif status == "DONE":
        status_string = status_string + '<span class="badge bg-success">'
    elif status == "FAILED":
        status_string = status_string + '<span class="badge bg-danger">'
    else:
        status_string = status_string + '<span class="badge bg-warning text-dark">'
    status_string = status_string + status
    status_string = status_string + '</span> '
    return status_string


### Build testrun overview webpage
def build(testrun_instance, single_testrun_path, page_template):
    single_testrun_path = os.path.join("testruns", testrun_instance)
    #response = "<html><title>Test Result Server</title><body><h2>TESTCASES OF TESTRUN: " + testrun_instance + "</h2><hr>"
    body="<b>&nbsp;Testrun: " + testrun_instance + """</b><br><table class="table">
  <thead>
    <tr>
      <th scope="col">Status</th>
      <th scope="col">Testlog</th>
      <th scope="col">Last status change</th>
      <th scope="col">Details</th>
    </tr>
  </thead>
  <tbody>
"""
    if os.path.exists(single_testrun_path):
       if len(os.listdir(single_testrun_path))!=0:
           for testcase_folder in sorted(os.listdir(single_testrun_path), reverse=True):
              testcase_path = os.path.join(single_testrun_path, testcase_folder)
              if os.path.isdir(testcase_path):
                  testrun_details = get_testcase_status(testcase_path)
                  current_local_time = time.asctime(time.localtime(testrun_details['timestamp']))
                  status_string = format_status_string(testrun_details["status"])
                  
                  body = body + "<tr>"
                  body = body + "<td>" + status_string + "</td>"
                  body = body + "<td>" + "<a href='/testruns/" + testrun_instance + "/" + testcase_folder + "/log.html'>" + testcase_folder + "</a>" + "</td>"
                  body = body + "<td>" + current_local_time + "</td>"
                  body = body + "<td>" + "<a href='/testruns/" + testrun_instance + "/" + testcase_folder + "/'>" + testcase_folder + "</a>" + "</td>" + "</td>"
                  body = body + "</tr>"
                  #body = body + "<a href='/testruns/" + testrun_instance + "/" + testcase_folder + "/'>" + testcase_folder + \
                  #            "</a> (" + status_string + " at " + current_local_time + ")<br>"
    
    
    body = body + "</tbody></table"
    page_template =  page_template.replace("{BODY}",body)
    return True, page_template