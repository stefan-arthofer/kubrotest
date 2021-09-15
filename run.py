#!/usr/bin/python3

import sys
import os
import yaml
import datetime
import subprocess

TOOL_KUBECTL = "kubectl"
DEFAULT_PROFILE = "standard"

def get_usage():
    return """
run.py <TESTCASE> <PROFILE>

e.g. run.py ALL standard

Arguments:
   [<TESTCASE>]   ... run single test case by name or default="ALL"
   [<PROFILE>]    ... standard, ...
   """
def check_for_help_agrument(argv, help_message):
    if len(argv) != 2:
        return
    if not argv[1] in ["--help", "-help", "-h", "--h", "/?"]:
        return
    print("Detail usage for " + os.path.basename(argv[0])+ ":\n" + help_message)
    exit(0)


def create_testrun_namespace():
    #Build String date-2021-03-30-time-13-13-57-ms-126690 from current time
    testrun_namespace = "date-" + \
            str(datetime.datetime.now()).replace(":", "-").replace(" ", "-time-").replace(".", "-ms-")
    print("#####################################################")
    print("Testrun Namespace: " + testrun_namespace)
    # kubectl create namespace <TESTRUN_NAMESPACE>
    result = subprocess.run([TOOL_KUBECTL, 'create', "namespace", testrun_namespace],
                            check=True, stderr=subprocess.STDOUT, stdout=sys.stdout)
    return testrun_namespace


def get_profile(profile_name):
    profile_root_path=os.path.join(".", "profiles")
    if not os.path.exists(profile_root_path):
        print("Error - Profile Path is invalid: " + profile_root_path)
        exit(-1)
    profile_file_path = os.path.join(profile_root_path, profile_name + ".yml")
    if not os.path.exists(profile_file_path):
        print("Error - Profile profile not found in: " + profile_file_path)
    profile=open(profile_file_path,"r").read()
    return profile

def create_configmap(testrun_namespace, testcase_name, testcase_path):
    testcase_config_map_path = os.path.join(testcase_path, "test")
    # kubectl create configmap <TESTCASE> --from-file=test 
    if os.path.isdir(testcase_config_map_path):
        result = subprocess.run([TOOL_KUBECTL, "create", "configmap", testcase_name, 
                                "--from-file=test", "--namespace="+testrun_namespace],
                                check=True, stderr=subprocess.STDOUT, stdout=sys.stdout, cwd=testcase_path)

def start_testcase(testrun_namespace, testcase_name, testcase_path, profile_name):
    config_file_path = os.path.join(testcase_path, "config.yml")
    with open(config_file_path, 'r') as stream:
        try:
            test_config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
        
    if "limited-profiles" in test_config:
        if len(test_config["limited-profiles"]) >0:
            if profile_name not in test_config["limited-profiles"]:
                print("#####################################################")
                print("Skip Testcase " + testcase_name + " for profile " + profile_name)
                return
    print("#####################################################")
    print("Start Testcase: " + testcase_name)

    create_configmap(testrun_namespace=testrun_namespace, testcase_name=testcase_name, testcase_path=testcase_path)

    
    profile = get_profile(profile_name)
    profile = profile.replace("{TESTCASE}",testcase_name)
    profile = profile.replace("{TAG}","latest")
    
    tmp_modified_profile_path = os.path.join(".", "tmp", testrun_namespace, testcase_name)
    os.makedirs(tmp_modified_profile_path)
    tmp_modified_profile_file = os.path.join(tmp_modified_profile_path, profile_name + ".yml")
    
    f_tmp=open(tmp_modified_profile_file, "w+")
    f_tmp.write(profile)
    f_tmp.close()
    result = subprocess.run([TOOL_KUBECTL, 'apply', "-f", tmp_modified_profile_file, "--namespace="+testrun_namespace], 
                   check=True, stderr=subprocess.STDOUT, stdout=sys.stdout)
    
    # kubectl apply -f XXXX.yml
    #for kube_yml in test_config['kube-yml']:
    #    result = subprocess.run([TOOL_KUBECTL, 'apply', "-f", kube_yml, "--namespace="+testrun_namespace], 
    #               stderr=subprocess.STDOUT, stdout=sys.stdout, cwd=testcase_path)
    
    
    print("Display current state of testrun: " + TOOL_KUBECTL + " get pods --namespace=" + testrun_namespace)
    print("Display current state of specific testcase: " + TOOL_KUBECTL + " describe pods --namespace=" +
          testrun_namespace + " " + testcase_name)
    print("Display current logs of specific testcase: log.py " + testrun_namespace + " " + testcase_name + 
          " robotframework")

def start_testrun(testcase_name_in, profile_name):
    start_testresultserver_if_nesscary()

    testcase_root_path=os.path.join(".", "testcases")
    if not os.path.exists(testcase_root_path):
        print("Error - Testcase Path is invalid: " + testcase_root_path)
        exit(-1)

    testrun_namespace = create_testrun_namespace()

    for testcase_name in os.listdir(testcase_root_path):
        if testcase_name_in != "ALL":
            if testcase_name != testcase_name_in:
                continue
        testcase_path = os.path.join(testcase_root_path, testcase_name)
        if os.path.isdir(testcase_path):
            start_testcase(testrun_namespace=testrun_namespace, testcase_name=testcase_name, testcase_path=testcase_path, profile_name=profile_name)
    print("#####################################################")
    print("Testresult can be found in http://localhost:30010/testruns/" + testrun_namespace)

def start_testresultserver_if_nesscary():
    profile_root_path=os.path.join(".", "profiles")

    testresultserver_namespace = "testresultserver"

    result = subprocess.run([TOOL_KUBECTL, "get", "pod", "testresultserver", "--namespace="+testresultserver_namespace, 
                                 "-o=jsonpath={.status.containerStatuses[0].ready}"], capture_output=True)
    if "true" in str(result.stdout):
       print("Testresultserver is already running")
       return
    #print(str(result.stdout))
    print("Testresultserver IS NOT running! We start the server first ... ")

    result = subprocess.run([TOOL_KUBECTL, 'create', "namespace", testresultserver_namespace],
                            check=True, stderr=subprocess.STDOUT, stdout=sys.stdout)
    result = subprocess.run([TOOL_KUBECTL, "apply", "-f", "testresultserver.yml", 
                            "--namespace="+testresultserver_namespace],
                            check=True, stderr=subprocess.STDOUT, stdout=sys.stdout, cwd=profile_root_path)


if __name__ == "__main__":
    check_for_help_agrument(sys.argv, get_usage())
    if len(sys.argv) > 3 or len(sys.argv) == 1:
        print("Error - Invalid Number of arguments")
        print(get_usage())
    elif len(sys.argv) == 2:
        start_testrun(testcase_name_in=sys.argv[1], profile_name=DEFAULT_PROFILE)
    elif len(sys.argv) == 3:
        start_testrun(testcase_name_in=sys.argv[1], profile_name=sys.argv[2])
    exit(0)
