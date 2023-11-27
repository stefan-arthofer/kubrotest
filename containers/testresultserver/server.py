#!/usr/bin/python3

import http.server
import socketserver
import io
import os
import sys
import cgi
import json
import time
import testrun_overview
import testrun_view
from threading import Thread, Lock

CIRITCAL_SECTION = Lock()

### Protects against path traversal attack
def is_safe_path(basedir, path):
  return os.path.abspath(path).startswith(basedir)

### Returns root path of webserver
def get_root_path():
  return os.getcwd()

### Returns foldername for testruns
def get_testruns_foldername():
  return "testruns"

### Returns full path of testruns folder
def get_testruns_path():
  return os.path.join(get_root_path(), get_testruns_foldername())

def get_page_template():
  return open("/page_template.html").read()


### Saves target file on file system
def save_uploaded_file(file_path, content):
   # create directory if not exists
   if not os.path.exists(os.path.dirname(file_path)):
      os.makedirs(os.path.dirname(file_path))
   try:
      f_w = open(file_path, "wb")
      f_w.write(content)
      f_w.close()
   except IOError:
      print("Error cant write uploaded file to " + file_path)

### Update status of a testcase
def update_status_file(testcase_status_file, status):
   # create directory if not exists
   if not os.path.exists(testcase_status_file):
       os.makedirs(os.path.dirname(testcase_status_file))
   
   # protect against simulation access of status files
   CIRITCAL_SECTION.acquire()
   try:
       status_list=[]
       if os.path.exists(testcase_status_file):
           f = open(testcase_status_file,"r")
           status_list = json.loads(f.read())
           f.close()
       status_list.append(status)
       f = open(testcase_status_file,"w+")
       f.write(json.dumps(status_list))
       f.close()
   
   finally:
       #release mutex
       CIRITCAL_SECTION.release()




### Process parallel http requests
class ThreadingSimpleServer(socketserver.ThreadingMixIn,
                   http.server.HTTPServer):
    pass

### Custom Handler for webserver
class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        uri_splitted = self.path.split("/")
        uri_splitted = list(filter(None, uri_splitted))
        # Build testrun overview webpage (Startpage)
        if len(uri_splitted)<2:
            f_success, response = testrun_overview.build(get_testruns_path(), get_page_template())
            self.send_reply(f_success=f_success, response=response)
            return
        # Build detail information webpage for target testrun
        elif uri_splitted[0] == "testruns" and len(uri_splitted)==2:
            testrun_instance = uri_splitted[1]
            single_testrun_path = os.path.join(get_testruns_path(), testrun_instance)
            f_success, response = testrun_view.build(testrun_instance, single_testrun_path, get_page_template())
            self.send_reply(f_success=f_success, response=response)
            return
                
        # Else: handle default webserver get implementation
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        content_len = int(self.headers['Content-Length'])
        # Update status of a testcase
        if self.path.startswith("/status/"):
            f_success = True
            status = json.loads(self.rfile.read(content_len).decode('utf-8'))
      
            # self.set_status(testcase_uri, status)
            response = "Status change for: " + self.path[8:] + " (" + json.dumps(status) + ")"
            
            testruns_path = get_testruns_path()
            testcase_status_file = os.path.join(testruns_path, self.path[8:], "status.txt")
            
            update_status_file(testcase_status_file=testcase_status_file, status=status)
            self.send_reply(f_success=f_success, response=response)
         
        # Upload testcase results
        elif self.path.startswith("/testruns/"):
            f_success, response = self.upload_testcase_results()
            self.send_reply(f_success=f_success, response=response)
        else:
            self.send_reply(f_success=False, response="Unkown command")
    
    ### General reply
    def send_reply(self, f_success, response):
        if f_success:
            # HTTP-Statuscode 200 OK
            self.send_response(200)
        else:
            # HTTP-Statuscode 400 Bad Request 
            self.send_response(400)
        
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes(response, 'utf-8'))
    
    ### Upload testcase results
    def upload_testcase_results(self):
        form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={
                                'REQUEST_METHOD': 'POST', 'CONTENT_TYPE': self.headers['Content-Type'], })
        upload_uri=self.path
        # remove leading "/" from uri (e.g. upload_uri = "/test/uri" -> "test/uri")
        if upload_uri[0] == "/":
            upload_uri = upload_uri[1:]

        info_message = ""
        testruns_path = get_testruns_path()
        root_path = get_root_path()

        try:
            if isinstance(form.value, list):
                for f in form.value:
                    file_path = os.path.join(root_path, upload_uri, f.filename)
                    if not is_safe_path(testruns_path, file_path):
                        return (False, "Invalid Upload (Transversal path injection detected)")
                    content = f.value
                    save_uploaded_file(file_path=file_path, content=content)

                    # Add filename for Info Message
                    if info_message != "":
                        info_message = info_message + ", "
                    info_message = info_message + file_path
            else:
                f = form.value
                file_path = os.path.join(root_path, upload_uri, f.filename)
                if not is_safe_path(testruns_path, file_path):
                    return (False, "Invalid Upload (Transversal path injection detected)")
                content = f.value
                save_uploaded_file(file_path=file_path, content=content)

                # Add filename for Info Message
                info_message = info_message + file_path

            return (True, "File(s) " + info_message + " upload success!")
        except IOError:
            return (False, "Can't create file to write, do you have permission to write?")

# Start webserver
def start_webserver():
    PORT = 80
    ROOT_PATH = os.path.join("/", "www")
    #ROOT_PATH = os.path.join("www")

    # Set timezone to middle europe 
    if hasattr(time, 'tzset'):
        os.environ['TZ'] = "CET-1CEST-2,M3.5.0/02:00:00,M10.5.0/03:00:00"
        time.tzset()
    
    # Set webserver root path (=current directory)
    os.chdir(ROOT_PATH)
    
    # Register Multithreaded Webserver
    server = ThreadingSimpleServer(('', PORT), CustomHTTPRequestHandler) 
    print("started httpserver...")
    try:
        while 1:
            sys.stdout.flush()
            server.handle_request()
    except KeyboardInterrupt:
        print("^C received, shutting down server")
        server.socket.close()

if __name__ == '__main__':
    print("Start Server")
    start_webserver()
