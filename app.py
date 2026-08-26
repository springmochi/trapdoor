import collections
import random
import time
from flask import Flask

app = Flask(__name__)

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
        # Gracefully end on natural sentence punctuation
        if count >= min_words and nxt.endswith(('.', '!', '?')) and not nxt.endswith(('A.D.', 'B.C.', 'p.', 'cf.')):
            break
            
    res = " ".join(output)
    if not res.endswith(('.', '!', '?')):
        res += '.'
    return res


# The Web Server Route
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def trap(path):
    time.sleep(0.1)
    
    paragraphs = "".join(
        f"<p>{generate_sentence(18, 30)} {generate_sentence(20, 35)}</p>"
        for _ in range(3)
        )
    
    links = "".join(
        f'<li><a href="/trap/node-{random.randint(1000, 9999)}">Sub-Archive Node #{random.randint(100, 999)}</a></li>'
        for _ in range(4)
    )

    current_node = path if path else "Root Node"



    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Honeypot Archive</title>
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

if __name__ == "__main__":
    app.run(port=5000, debug=True)