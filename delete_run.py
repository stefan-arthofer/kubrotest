#!/usr/bin/python3

import sys
import os
import yaml
import datetime
import subprocess

TOOL_KUBECTL = "kubectl"
# https://kubernetes.io/docs/reference/generated/kubectl/kubectl-commands#apply

def get_usage():
    return """
delete_run.py <TESTRUN_NAMESPACE>
   
Arguments:
   <TESTRUN_NAMESPACE>   ... Namespace of testrun  (USE ALL to delete all testcases)
   """

def check_for_help_agrument(argv, help_message):
    if len(argv) != 2:
        return
    if not argv[1] in ["--help", "-help", "-h", "--h", "/?"]:
        return
    print("Detail usage for " + os.path.basename(argv[0])+ ":\n" + help_message)
    exit(0)

def delete_all_testruns():
   result = subprocess.run([TOOL_KUBECTL, 'get', "namespace", "-o", "jsonpath='{.items[*].metadata.name}'"],
                        capture_output=True)
   testrun_namespace_list = str(result.stdout).split(" ")
   for testrun_namespace in testrun_namespace_list:
      #testrun a usual namespace looks like this date-2021-03-29-time-07-19-18-ms-179720
      if "date-" in testrun_namespace and "-time-" in testrun_namespace and "-ms-" in testrun_namespace:
         delete_single_testrun(testrun_namespace)

def delete_single_testrun(testrun_namespace):
   result = subprocess.run([TOOL_KUBECTL, "delete", "namespace", testrun_namespace],
                            stderr=subprocess.STDOUT, stdout=sys.stdout)

if __name__ == "__main__":
    check_for_help_agrument(sys.argv, get_usage())
    if len(sys.argv) != 2:
        print("Error - Invalid Number of arguments")
        print(get_usage())
    elif len(sys.argv) == 2:
        if sys.argv[1].upper() == "ALL":
           delete_all_testruns()
        else:
           delete_single_testrun(testrun_namespace=sys.argv[1])
    exit(0)
