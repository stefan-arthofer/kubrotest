FROM python:3.8-slim

#RUN mkdir /www
COPY server.py /server.py
COPY testrun_overview.py /testrun_overview.py
COPY testrun_view.py /testrun_view.py
COPY page_template.html /page_template.html
RUN chmod +x /server.py /testrun_overview.py /testrun_view.py

RUN dir

#ENTRYPOINT ["/bin/sh"]
ENTRYPOINT ["python3", "/server.py"]