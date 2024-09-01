from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import random
import string

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a real secret key in production

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('urls.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS urls
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  original_url TEXT NOT NULL,
                  short_url TEXT NOT NULL)''')
    conn.commit()
    conn.close()

init_db()

def generate_short_url():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(6))

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        original_url = request.form['url']
        short_url = generate_short_url()

        conn = sqlite3.connect('urls.db')
        c = conn.cursor()
        c.execute("INSERT INTO urls (original_url, short_url) VALUES (?, ?)",
                  (original_url, short_url))
        conn.commit()
        conn.close()

        session['short_url'] = request.host_url + short_url
        return redirect(url_for('index'))
    
    short_url = session.get('short_url')
    return render_template('index.html', short_url=short_url)

@app.route('/<short_url>')
def redirect_to_url(short_url):
    conn = sqlite3.connect('urls.db')
    c = conn.cursor()
    result = c.execute("SELECT original_url FROM urls WHERE short_url = ?", (short_url,)).fetchone()
    conn.close()

    if result:
        return redirect(result[0])
    else:
        return "URL not found", 404

@app.route('/refresh')
def refresh():
    session.pop('short_url', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)