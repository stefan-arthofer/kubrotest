#!/usr/bin/python3
# python program for building container

import os
import sys
import subprocess

TOOL = "docker"

def get_usage():
    return """
build.py <VERSION_TAG> [<CONTAINER_NAME>]
   
   Build Target container
   
Arguments:
   <VERSION_TAG>      ... Version Tag 
   <CONTAINER_NAME>   ... Subfolder Name of "Containers"-Folder (optional, if not present build all existing)
"""

def check_for_help_agrument(argv, help_message):
    if len(argv) != 2:
        return False
    if not argv[1] in ["--help", "-help", "-h", "--h", "/?"]:
        return False
    print("Detail usage for " + os.path.basename(argv[0])+ ":\n" + help_message)
    exit(0)

def build_all_containers(version_tag, root_containers_path):
    for subfolder in os.listdir(root_containers_path):
        dockerfile_path = os.path.join(
            root_containers_path, subfolder, "Dockerfile")
        container_name = subfolder
        print("----------------------------------")
        if os.path.exists(dockerfile_path):
            build_single_container(
                version_tag=version_tag, dockerfile_path=dockerfile_path, container_name=container_name)
        else:
            print("SKIP invalid path: " + dockerfile_path)


def build_single_container(version_tag, dockerfile_path, container_name):
    if not os.path.exists(dockerfile_path):
        print("Error - Dockerfile could not be found in: " + dockerfile_path)
        exit(-2)

    build_tag = container_name + ":" + version_tag
    print("BUILD: " + dockerfile_path + " with tag '" + build_tag + "'")
    dockerfile_path_root = os.path.dirname(dockerfile_path)
    result = subprocess.run([TOOL, 'build', '-t', build_tag,
                             dockerfile_path_root], stderr=subprocess.STDOUT, stdout=sys.stdout)


if __name__ == "__main__":
    # TODO if help is in argv? -> print get usage
    if len(sys.argv) > 4:
        print("Error - Invalid Number of arguments")
        print(get_usage())
        exit(-1)

    # get root path of script
    root_containers_path = os.path.join(os.path.dirname(__file__), "containers")
    if len(sys.argv) == 1:
        build_all_containers(
            version_tag="latest", root_containers_path=root_containers_path)
    if len(sys.argv) == 2:
        build_all_containers(
            version_tag=sys.argv[1], root_containers_path=root_containers_path)
    elif len(sys.argv) == 3:
        container_name = sys.argv[2].lower()
        build_single_container(version_tag=sys.argv[1], dockerfile_path=os.path.join(
            root_containers_path, container_name, "Dockerfile"), container_name=container_name)
    exit(0)
