#!/usr/bin/env python3

from moz_sql_parser import parse as ransql_parse
from kafka import KafkaConsumer
import websockets
import http.server
import socketserver
import urllib.parse as url_parse
import json
import asyncio
import datetime
import random
import threading
import subprocess


#import re

def exe_cmd(cmd):
    try:
        print("shell: ", cmd)    
        subprocess.call(cmd, shell=True)
        
    except Exception as e:    
        print("exe_cmd error:", e)

def dispath_service(service_items):
    print("services to dispatch:",service_items)
    """
    {"select": {"value": {"avg": "total_pdu_bytes_rx"}}, "from": "eNB1", "where": {"eq": ["crnti", 0]}}
    {"select": {"value": {"add": ["ul", "dl"]}, "name": "total"}, "from": "eNB", "orderby": {"value": "total", "sort": "desc"}, "limit": [1, 10]}
    
    print("select:", service_items['select'])
    print("from:", service_items['from'])
    print("where:", service_items['where'])
    print("where:", service_items['where'])
    """


class RequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_HEAD(self):
        self._set_headers(200)

    def _set_headers(self, status_code):
        self.send_response(status_code)
        self.send_header('Content-type', 'text/html')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    def do_GET(self):
        request_path = self.path
        #print("request_path:",urllib.parse.unquote(request_path))
        payload =  url_parse.unquote(request_path)
        payload = payload[5:-1]
        
        print('request params:', payload ) #remove /?q=" at the begin and " at the end

        if payload == "cancel-usecase-1":
            #TODO
            content = self._handle_http(201, "cancel_usecase_1_ok")
            self.wfile.write(content)

        elif payload =="cancel-usecase-2":
            #TODO
            content = self._handle_http(202, "cancel_usecase_2_ok")
            self.wfile.write(content)

        else:
            try:
                sql_in_json = json.dumps(ransql_parse(payload))
                
                dispath_service(sql_in_json)
                content = self._handle_http(200, "parse_ok")
                
                self.wfile.write(content)

            except Exception as e:
                print(e)
                content = self._handle_http(404, "parse_error")
                self.wfile.write(content)
                

    def _handle_http(self, status_code, message):
        #self.send_response(status_code)
        self._set_headers(status_code)
        content = message
        return bytes(content, 'UTF-8')

        
def run_http_server(port=8888):
    requestHandler = RequestHandler#http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), requestHandler) as httpd:
        print("serving at port", port)
        httpd.serve_forever()


async def websocket_handler(websocket, path):
    kafka_topic = "oai-final"
    kafka_group = "oai"
    kafka_brokers = "192.168.200.3:9092"
    
    #consumer = KafkaConsumer(kafka_topic, auto_offset_reset='latest',enable_auto_commit=False, group_id=kafka_group, bootstrap_servers=[kafka_brokers])

    while True:
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        await websocket.send(now)
        await asyncio.sleep(random.random() * 3)
    
async def myfun1():    
    print('-- start {}th'.format(2))    
    await asyncio.sleep(3)    
    #time.sleep(1)
    print('-- finish {}th'.format(2))



    
if __name__ == "__main__":
    """
    pass configuration
    """


    #https://stackoverflow.com/questions/26270681/can-an-asyncio-event-loop-run-in-the-background-without-suspending-the-python-in
    #https://youtu.be/L3RyxVOLjz8
    #loop = asyncio.get_event_loop()
    #t = threading.Thread(target=loop_in_thread, args=(loop,))
    #t.start()

    t_http_server = threading.Thread(target=run_http_server)
    t_http_server.daemon = True
    t_http_server.start()


    """

    if len(sys.argv) == 2:
        run_http_server(port=int(argv[1]))
    else:
        run_http_server()
    """

    websocket_server = websockets.serve(websocket_handler, '0.0.0.0', 5678)
    coroutines = (websocket_server, myfun1())


    asyncio.get_event_loop().run_until_complete(asyncio.gather(*coroutines))
    asyncio.get_event_loop().run_forever()
