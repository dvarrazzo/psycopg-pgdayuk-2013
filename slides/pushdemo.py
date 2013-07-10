import sys

import gevent
from gevent import pywsgi
from gevent.queue import Queue
from gevent.socket import wait_read
from geventwebsocket.handler import WebSocketHandler

import psycopg2
from psycogreen.gevent import patch_psycopg
patch_psycopg()

dsn = "dbname=test"  # customise this or pass a dsn to the script

if len(sys.argv) > 1:
    dsn = sys.argv[1]

queues = set()

def dblisten():
    conn = psycopg2.connect(dsn)
    conn.autocommit = True

    cur = conn.cursor()
    cur.execute('listen data')
    cur.close()

    while 1:
        wait_read(conn.fileno(), timeout=None)
        conn.poll()
        while conn.notifies:
            n = conn.notifies.pop()
            print "received notify:", n
            for q in queues:
                q.put(n)

def watcher(ws, q):
    """Detect a disconnection and close the client queue"""
    try:
        q.put(ws.receive())
    except Exception:
        # assume disconnected
        q.put(None)

def handle_client(ws):
    q = Queue()
    print "queue added:", id(q)
    queues.add(q)
    gevent.spawn(watcher, ws, q)

    try:
        while True:
            n = q.get()
            if n is None:
                break
            ws.send(n.payload)
    finally:
        print "queue removed:", id(q)
        queues.remove(q)

def app(environ, start_response):
    if environ['PATH_INFO'] == "/data":
        handle_client(environ['wsgi.websocket'])
    elif environ['PATH_INFO'] == "/":
        start_response('200 OK', [('Content-Type', 'text/html')])
        return [page]
    else:
        print "404, PATH_INFO: %s" %  environ["PATH_INFO"]
        start_response("404 Not Found", [])
        return []

page = """
<html>
  <head><title>pushdemo</title>
    <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.4.1/jquery.min.js"></script>
    <style type="text/css">
      .bar {width: 20px; height: 20px;}
    </style>
    <script>
      window.onload = function() {
        ws = new WebSocket("ws://localhost:7000/data");
        console.log('connected');
        ws.onmessage = function(msg) {
          bar = $('#' + msg.data);
          bar.width(bar.width() + 10);
        }
      }
    </script>
  </head>
  <body>
    <div style="width: 400px;">
      <div id="red" class="bar"
          style="background-color: red;">&nbsp;</div>
      <div id="green" class="bar"
          style="background-color: green;">&nbsp;</div>
      <div id="blue" class="bar"
          style="background-color: blue;">&nbsp;</div>
    </div>
  </body>
</html>
"""

if __name__ == "__main__":
    addr = ('127.0.0.1', 7000)
    gevent.spawn(dblisten)
    server = pywsgi.WSGIServer(addr, app, handler_class=WebSocketHandler)
    server.serve_forever()

