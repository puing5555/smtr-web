"""Simple HTTP server to receive transcript data from browser"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers['Content-Length'])
        data = self.rfile.read(length)
        
        # Parse the path for filename
        filename = self.path.strip('/')
        filepath = f'C:/Users/Mario/work/subs/{filename}'
        
        with open(filepath, 'wb') as f:
            f.write(data)
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(b'OK')
        print(f'Saved {len(data)} bytes to {filepath}')
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

server = HTTPServer(('127.0.0.1', 18888), Handler)
print('Listening on http://127.0.0.1:18888')
server.handle_request()  # Handle one request then exit
server.handle_request()  # OPTIONS + POST
print('Done')
