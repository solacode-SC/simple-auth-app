from flask import Flask, render_template, request, redirect, session, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'mysecret'  # Needed for sessions

def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    return redirect('/login')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Validate input
        if not username or not password:
            flash('Please fill in all fields')
            return render_template('signup.html')
        
        if len(username) < 3:
            flash('Username must be at least 3 characters long')
            return render_template('signup.html')
        
        if len(password) < 4:
            flash('Password must be at least 4 characters long')
            return render_template('signup.html')
        
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        try:
            c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
            flash('Account created successfully! Please log in.', 'success')
            return redirect('/login')
        except sqlite3.IntegrityError:
            flash('Username already exists. Please choose a different username.')
            return render_template('signup.html')
        finally:
            conn.close()
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if not username or not password:
            flash('Please fill in all fields')
            return render_template('login.html')
        
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            session['user'] = username
            flash('Welcome back!', 'success')
            return redirect('/profile')
        else:
            flash('Invalid username or password')
            return render_template('login.html')
    return render_template('login.html')

@app.route('/profile')
def profile():
    if 'user' not in session:
        return redirect('/login')
    return render_template('profile.html', username=session['user'])

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
