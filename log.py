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
log.py <TESTRUN_NAMESPACE> <TESTCASE>
   
Arguments:
   <TESTRUN_NAMESPACE>   ... Namespace of testrun  (USE ALL to delete all testcases)
   <TESTCASE>            ... 
   """

def check_for_help_agrument(argv, help_message):
    if len(argv) != 2:
        return
    if not argv[1] in ["--help", "-help", "-h", "--h", "/?"]:
        return
    print("Detail usage for " + os.path.basename(argv[0])+ ":\n" + help_message)
    exit(0)

def log_testcase(testrun_namespace, testcase):
   result = subprocess.run([TOOL_KUBECTL, "logs", "--namespace="+testrun_namespace, testcase],
                            stderr=subprocess.STDOUT, stdout=sys.stdout)

def log_testcase_container(testrun_namespace, testcase, container):
   result = subprocess.run([TOOL_KUBECTL, "logs", "--namespace="+testrun_namespace, testcase, container],
                            stderr=subprocess.STDOUT, stdout=sys.stdout)

if __name__ == "__main__":
    check_for_help_agrument(sys.argv, get_usage())
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print("Error - Invalid Number of arguments")
        print(get_usage())
    elif len(sys.argv) == 3:
        log_testcase(testrun_namespace=sys.argv[1], testcase=sys.argv[2])
        print("e.g. log.py " + sys.argv[1] + " " + sys.argv[2], "<CONTAINER>")
    elif len(sys.argv) == 4:
        log_testcase_container(testrun_namespace=sys.argv[1], testcase=sys.argv[2], container=sys.argv[3])
    exit(0)
