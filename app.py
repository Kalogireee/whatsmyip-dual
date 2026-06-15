from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import subprocess
from datetime import datetime
import os
import time

PORT = int(os.getenv("PORT", "3464"))

IP_MODE = os.getenv("IP_MODE", "both").lower().strip()

VALID_MODES = ["both", "ipv4", "ipv6"]

if IP_MODE not in VALID_MODES:
    IP_MODE = "both"

def should_show_ipv4():
    return IP_MODE in ["both", "ipv4"]

def should_show_ipv6():
    return IP_MODE in ["both", "ipv6"]

def get_local_time():
    return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")

def get_public_ip(version):
    if version == 4:
        curl_flag = "-4"
        url = "https://api.ipify.org"
    else:
        curl_flag = "-6"
        url = "https://api64.ipify.org"

    try:
        ip = subprocess.check_output(
            [
                "curl",
                curl_flag,
                "-s",
                "--max-time", "2",
                url
            ],
            stderr=subprocess.DEVNULL,
            timeout=3
        ).decode().strip()

        if not ip:
            return "Not available", "Unavailable", False

        return ip, "OK", True

    except Exception:
        return "Not available", "Unavailable", False

def render_card(label, ip, status, available):
    card_class = "card available" if available else "card unavailable"
    ip_class = "ip available-text" if available else "ip unavailable-text"

    return f"""
    <div class="{card_class}">
      <div class="label">{label}</div>
      <div class="{ip_class}">{ip}</div>
      <div class="status">Status: {status}</div>
    </div>
"""

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        page_refresh_time = get_local_time()

        cards = ""

        if should_show_ipv4():
            ipv4, ipv4_status, ipv4_available = get_public_ip(4)
            cards += render_card("Public IPv4 Address", ipv4, ipv4_status, ipv4_available)

        if should_show_ipv6():
            ipv6, ipv6_status, ipv6_available = get_public_ip(6)
            cards += render_card("Public IPv6 Address", ipv6, ipv6_status, ipv6_available)

        mode_display = IP_MODE.upper()
        timezone_display = time.tzname[0]

        html = f"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Public IP Address</title>
  <style>
    body {{
      font-family: Arial, sans-serif;
      margin: 40px;
      background: #111;
      color: #eee;
    }}
    .container {{
      max-width: 1000px;
    }}
    .card {{
      margin-bottom: 32px;
      padding: 24px;
      background: #1a1a1a;
      border-radius: 12px;
      border: 1px solid #333;
    }}
    .card.unavailable {{
      border-color: #7f1d1d;
      background: #1a1111;
    }}
    .label {{
      color: #aaa;
      font-size: 18px;
      margin-bottom: 10px;
    }}
    .ip {{
      font-size: 32px;
      font-weight: bold;
      margin: 10px 0;
      word-break: break-all;
    }}
    .available-text {{
      color: #4ade80;
    }}
    .unavailable-text {{
      color: #f87171;
    }}
    .info {{
      color: #aaa;
      font-size: 16px;
      margin-top: 10px;
    }}
    .status {{
      color: #60a5fa;
      font-size: 16px;
      margin-top: 10px;
    }}
  </style>
</head>
<body>
  <div class="container">
    <h1>Public IP Address</h1>

    {cards}

    <div class="info">Mode: {mode_display}</div>
    <div class="info">Page refreshed at: {page_refresh_time}</div>
    <div class="info">Local timezone: {timezone_display}</div>
  </div>
</body>
</html>
"""

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.end_headers()
        self.wfile.write(html.encode())

    def log_message(self, format, *args):
        return

ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
