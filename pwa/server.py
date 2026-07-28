import http.server, socketserver, urllib.request, urllib.error, os, socket, sys, json

STREAMLIT_URL = "https://stock-analysis.streamlit.app"
PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PWA_DIR = os.path.join(PROJ, "pwa")
PORT = 8080

def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def proxy_request(self):
    path = self.path
    if path.startswith("/app"):
        url = STREAMLIT_URL + "/"
    else:
        url = STREAMLIT_URL + path
    method = self.command
    try:
        if method == "GET":
            req = urllib.request.Request(url, headers=dict(self.headers))
        elif method == "POST":
            length = int(self.headers.get("content-length", 0))
            body = self.rfile.read(length)
            req = urllib.request.Request(url, data=body, headers=dict(self.headers), method="POST")
        resp = urllib.request.urlopen(req, timeout=30)
        self.send_response(resp.status)
        for k, v in resp.getheaders():
            lk = k.lower()
            if lk not in ("transfer-encoding", "content-encoding", "content-length", "connection"):
                self.send_header(k, v)
        self.end_headers()
        self.wfile.write(resp.read())
    except urllib.error.HTTPError as e:
        self.send_response(e.code)
        self.end_headers()
        self.wfile.write(e.read())
    except Exception as e:
        self.send_error(502, "Proxy error: " + str(e))

class PWAHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split("?")[0]
        pwa_file = os.path.join(PWA_DIR, path.lstrip("/"))
        if os.path.isfile(pwa_file):
            self.directory = PWA_DIR
            return http.server.SimpleHTTPRequestHandler.do_GET(self)
        proxy_request(self)
    def do_POST(self):
        proxy_request(self)

ip = get_ip()
print("=== Stock Analysis PWA ===")
print("Streamlit: " + STREAMLIT_URL)
print("PWA: http://" + ip + ":" + str(PORT))
print()
print("On your phone:")
print("  Open http://" + ip + ":" + str(PORT))
print("  iOS: Share > Add to Home Screen")
print("  Android: Menu > Add to Home Screen")
print()

with socketserver.TCPServer(("0.0.0.0", PORT), PWAHandler) as httpd:
    httpd.serve_forever()
