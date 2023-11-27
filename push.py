#!/usr/bin/python3

import os
import sys
import subprocess

TOOL = "docker"

def get_usage():
    return """
push.py <VERSION> <REGISTRY>
   
   Build Target container
   
Arguments:
   <VERSION>        ... Version Tag
   <REGISTRY>       ... Registry
"""
def check_for_help_agrument(argv, help_message):
    if len(argv) != 2:
        return
    if not argv[1] in ["--help", "-help", "-h", "--h", "/?"]:
        return
    print("Detail usage for " + os.path.basename(argv[0])+ ":\n" + help_message)
    exit(0)

def push_all_containers(version_tag, registry, root_containers_path):
    for subfolder in os.listdir(root_containers_path):
        dockerfile_path = os.path.join(
            root_containers_path, subfolder, "Dockerfile")
        container_name = subfolder
        print("----------------------------------")
        if os.path.exists(dockerfile_path):
            push_single_container(
                version_tag=version_tag, registry=registry, dockerfile_path=dockerfile_path, container_name=container_name)
        else:
            print("SKIP invalid path: " + dockerfile_path)


def push_single_container(version_tag, registry, dockerfile_path, container_name):
    if not os.path.exists(dockerfile_path):
        print("Error - Dockerfile could not be found in: " + dockerfile_path)
        exit(-2)

    source_tag = container_name + ":" + version_tag
    push_tag = registry + "/" + container_name + ":" + version_tag
    print("TAG: push " + source_tag + " to tag '" + push_tag + "'")
    dockerfile_path_root = os.path.dirname(dockerfile_path)
    result = subprocess.run([TOOL, 'tag', source_tag, push_tag], stderr=subprocess.STDOUT, stdout=sys.stdout)
    print(TOOL + " push " + push_tag)
    result = subprocess.run([TOOL, 'push', push_tag], stderr=subprocess.STDOUT, stdout=sys.stdout)


if __name__ == "__main__":
    check_for_help_agrument(sys.argv, get_usage())
    if len(sys.argv) > 3 or len(sys.argv) == 1:
        print("Error - Invalid Number of arguments")
        print(get_usage())
        exit(-1)

    # get root path of script
    root_containers_path = os.path.join(
        os.path.dirname(__file__), "containers")
    if len(sys.argv) == 4:
        container_name = sys.argv[2].lower()
        push_single_container(version_tag=sys.argv[1], dockerfile_path=os.path.join(
            root_containers_path, container_name, "Dockerfile"), container_name=container_name)
    elif len(sys.argv) == 3:
        push_all_containers(
            version_tag=sys.argv[1], registry=sys.argv[2], root_containers_path=root_containers_path)
    exit(0)
