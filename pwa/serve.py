import http.server, socketserver, os, sys
PORT = 8080
DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pwa")
os.chdir(DIR)
Handler = http.server.SimpleHTTPRequestHandler
with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
    print("PWA server at http://0.0.0.0:" + str(PORT))
    print("Streamlit app at http://localhost:8501")
    httpd.serve_forever()
