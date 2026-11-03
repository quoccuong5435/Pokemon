"""Tiny local receiver: the browser POSTs each type icon PNG here (the shell cannot reach static.wikia.nocookie.net).
Files are only written into analysis/type_icons_fandom/ (name = last path part, letters only). Stops after 18 files or 120 s."""
import http.server
import os
import re
import threading
import time

OUT = os.path.join('analysis', 'type_icons_fandom')
os.makedirs(OUT, exist_ok=True)
got = set()


class H(http.server.BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Access-Control-Allow-Private-Network', 'true')

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_POST(self):
        name = re.sub(r'[^A-Za-z]', '', self.path.strip('/'))[:20]
        n = int(self.headers.get('Content-Length', 0))
        data = self.rfile.read(n)
        if name and data[:8] == b'\x89PNG\r\n\x1a\n' and n < 200000:
            open(os.path.join(OUT, name + '.png'), 'wb').write(data)
            got.add(name)
            self.send_response(200)
        else:
            self.send_response(400)
        self._cors()
        self.end_headers()

    def log_message(self, *a):
        pass


srv = http.server.HTTPServer(('127.0.0.1', 8765), H)
threading.Thread(target=srv.serve_forever, daemon=True).start()
t0 = time.time()
while len(got) < 18 and time.time() - t0 < 120:
    time.sleep(0.5)
srv.shutdown()
print('received', len(got), sorted(got))
