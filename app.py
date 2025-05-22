from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import pymysql

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'beverage'  # changed from 'flask' to 'beverage'
}

def get_db_connection():
    return pymysql.connect(
        host=db_config['host'],
        user=db_config['user'],
        password=db_config['password'],
        database=db_config['database']
    )

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['username'] = user[1]
            return redirect(url_for('homepage', username=user[1]))
        else:
            flash('Invalid credentials. Please try again.')
    return render_template('login.html')

@app.route('/homepage')
def homepage():
    return render_template('homepage.html', username=session.get('username'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password1']
        password2 = request.form['password2']

        errors = []

        if not username or not password or not password2:
            errors.append("All fields are required.")
        elif password != password2:
            errors.append("Passwords do not match.")

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()

        if user:
            errors.append("Username is already taken.")

        if errors:
            return render_template('register.html', username=username, errors=errors)

        cursor.execute("INSERT INTO users(username, password) VALUES (%s, %s)", (username, password))
        conn.commit()
        conn.close()

        flash("Registration successful. Please log in.")
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for('login'))

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        username = request.form['username']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cur.fetchone()
        conn.close()

        if user:
            return render_template('password-reset.html', username=username)
        else:
            flash('User does not exist.', 'error')

    return render_template('forgot-password.html')

@app.route('/password_reset', methods=['GET', 'POST'])
def password_reset():
    if request.method == 'POST':
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        if password1 != password2:
            flash("Passwords do not match.")
            return render_template('password-reset.html', password1=password1, username=username)

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('UPDATE users SET password=%s WHERE username=%s', (password1, username))
        conn.commit()
        conn.close()

        flash('Password successfully updated. You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('password-reset.html')

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    product = request.json
    if 'cart' not in session:
        session['cart'] = []
    cart = session['cart']
    cart.append(product)
    session['cart'] = cart
    return jsonify({'success': True, 'cart_count': len(cart)})

@app.route('/cart')
def get_cart():
    cart = session.get('cart', [])
    return jsonify({'cart': cart, 'cart_count': len(cart)})

if __name__ == '__main__':
    app.run(debug=True)
