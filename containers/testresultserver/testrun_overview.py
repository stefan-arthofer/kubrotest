#!/usr/bin/python3

import os
import sys
import json


def get_testcase_status_summary(testrun_path):
   testrun_status_summary={}
   for subfolder in sorted(os.listdir(testrun_path), reverse=True):
      testcase_status_file = os.path.join(testrun_path, subfolder, "status.txt")
      if os.path.exists(testcase_status_file):
           f = open(testcase_status_file,"r")
           testcase_status_list = json.loads(f.read())
           f.close()
           testcase_status = testcase_status_list[-1]
           status = testcase_status['status'] 
           if status in testrun_status_summary.keys():
               testrun_status_summary[status] = testrun_status_summary[status] + 1
           else:
               testrun_status_summary[status] = 1
      else:
         # if status file for testcase not find -> return 'UNKNOWN' status
         if "UNKNOWN" in testrun_status_summary.keys():
            testrun_status_summary["UNKNOWN"] = testrun_status_summary["UNKNOWN"] + 1
         else:
            testrun_status_summary["UNKNOWN"] = 1
   return testrun_status_summary

def format_status_string(testrun_status_summary):
    status_string = ""
    for status in testrun_status_summary:
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
        status_string = status_string + str(testrun_status_summary[status]) + " - " + status
        status_string = status_string + '</span> '
    return status_string
### Build testrun overview webpage
def build(testruns_path, page_template):
    body="""<table class="table">
  <thead>
    <tr>
      <th scope="col">Testrun</th>
      <th scope="col">Status</th>
    </tr>
  </thead>
  <tbody>
"""

    if os.path.exists(testruns_path):
       if len(os.listdir(testruns_path))!=0:
           for subfolder in sorted(os.listdir(testruns_path), reverse=True):
               full_subfolder_path = os.path.join(testruns_path, subfolder)
               if os.path.isdir(full_subfolder_path):
                   testrun_status_summary = get_testcase_status_summary(full_subfolder_path)
                   status_string = format_status_string(testrun_status_summary)
                   body = body + "<tr>"
                   body = body + "<td>" + "<a href='testruns/" + subfolder + "/'>" + subfolder + "</a> " + "</td>"
                   body = body + "<td>" + status_string + "</td>"
                   body = body + "</tr>"
                   #body = body + "<a href='testruns/" + subfolder + "/'>" + subfolder + "</a> " + status_string + " <br>"
                              #json.dumps(testrun_status_summary).replace('"','').replace('{','').replace('}','') + ")<br>"
    page_template =  page_template.replace("{BODY}",body)

    #response = response + "</body></html>"
    return True, page_template