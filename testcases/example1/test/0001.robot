# import section for python libs
*** Settings ***
Library  liblog.py

# testcase section
*** Test Cases ***
Keyword Arguments
    liblog  "Hello World"
    liblog  "Log Message 22                 
