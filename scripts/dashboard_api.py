# Dashboard API (Server)
# ======================
# Simple HTTP server to route dashboard input to the steering file.
# Usage: python scripts/dashboard_api.py

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os

PORT = 8007
STEERING_FILE = "scripts/amr_steering.md"

class DashboardHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        if self.path == '/steer':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data)
                directive = data.get("directive", "")
                
                # Update steering file
                with open(STEERING_FILE, "w") as f:
                    f.write(f"**Current Directive**: {directive}\n\n**Priority**: HIGH\n\n**User Notes**:\n- [ ] Auto-generated from Dashboard.\n")
                
                print(f"Steering updated: {directive}")
                
                self.send_response(200)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(b'{"status": "ok"}')
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f'{{"error": "{str(e)}"}}'.encode())

    def do_GET(self):
        # Serve the heartbeat log for the dashboard to read
        if self.path == '/heartbeat':
            try:
                log_path = ".logs/heartbeat.jsonl"
                if os.path.exists(log_path):
                    with open(log_path, "r") as f:
                        lines = f.readlines()
                        last_line = lines[-1] if lines else "{}"
                    self.send_response(200)
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(last_line.encode())
                else:
                    self.send_response(404)
                    self.end_headers()
            except Exception:
                self.send_response(500)
                self.end_headers()

if __name__ == "__main__":
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, DashboardHandler)
    print(f"Dashboard API serving at http://localhost:{PORT}")
    httpd.serve_forever()
