FROM python:3.8-slim

RUN python3 -m pip install robotframework xmltodict requests

RUN mkdir /testresult
COPY testlib /testlib
COPY testtool /testtool
#directory current testcase is mounted as config map 

WORKDIR /

ENTRYPOINT ["python", "/testtool/start_test.py"]
