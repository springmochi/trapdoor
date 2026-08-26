import collections
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import random
import time

# Source vocabulary text
with open("corpus.txt", "r", encoding="utf-8") as f:
    CORPUS = f.read()

# Build the Markov table using defaultdict
possibles = collections.defaultdict(list)
w1 = w2 = ''
for word in CORPUS.split():
    possibles[w1, w2].append(word)
    w1, w2 = w2, word

possibles[w1, w2].append('')
possibles[w2, ''].append('')

# Filter for capitalized prefixes
capital_starters = [k for k in possibles if k[0][:1].isupper()]

# Sentence generator function
def generate_sentence(min_words=18, max_words=36):
    w1, w2 = random.choice(capital_starters)
    output = [w1, w2]
    
    for count in range(max_words):
        nxt = random.choice(possibles[w1, w2])
        if not nxt:
            break
        output.append(nxt)
        w1, w2 = w2, nxt

 # End on natural sentence punctuation
        if count >= min_words and nxt.endswith(('.', '!', '?')) and not nxt.endswith(('A.D.', 'B.C.', 'p.', 'cf.')):
            break
            
    res = " ".join(output)
    if not res.endswith(('.', '!', '?')):
        res += '.'
    return res


# HTTP request handler
class HoneypotHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        time.sleep(0.1)

# Get the visited path
        current_node = (
            self.path.lstrip("/") if self.path.strip("/") else "archive-root"
        )

        paragraphs = "".join(
            f"<p>{generate_sentence(18, 30)} {generate_sentence(20, 35)}</p>"
            for _ in range(3)
        )

        links = "".join(
            f'<li><a href="/archive/node-{random.randint(1000, 9999)}">Sub-Archive Node #{random.randint(100, 999)}</a></li>'
            for _ in range(4)
        )

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Hidden Archive</title>
    <style>
        body {{
            background: #121212;
            color: #d0d0d0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", monospace;
            max-width: 680px;
            margin: 40px auto;
            padding: 0 20px;
            line-height: 1.6;
        }}
        h2 {{ color: #ffffff; border-bottom: 1px solid #333; padding-bottom: 8px; }}
        a {{ color: #61afef; }}
        ul {{ list-style-type: square; line-height: 1.8; }}
        .badge {{ background: #222; padding: 3px 8px; border-radius: 4px; font-size: 0.8rem; color: #888; }}
    </style>
</head>
<body>
    <span class="badge">DEEP ARCHIVE NODE</span>
    <h2>Archive Reference: <code>{current_node}</code></h2>
    <article>{paragraphs}</article>
    <hr style="border:0; border-top: 1px solid #333; margin: 24px 0;">
    <h3>Discovered Sub-Directories:</h3>
    <ul>{links}</ul>
</body>
</html>"""

# Convert to bytes and send standard HTTP response headers
        body_bytes = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body_bytes)))
        self.end_headers()
        self.wfile.write(body_bytes)

# Suppress default terminal access logs
    def log_message(self, format, *args):
        print(f"[TRAP HIT] {self.address_string()} - {args[0]}")

if __name__ == "__main__":
    host = "127.0.0.1"
    port = 5000  

    server = ThreadingHTTPServer((host, port), HoneypotHandler)
    print(f"Running on http://{host}:{port}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nBye bye.")
        server.server_close()