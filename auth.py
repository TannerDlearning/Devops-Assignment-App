from flask import Blueprint, render_template, request, redirect, session, flash
import db

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        conn = db.get_connection()
        try:
            conn.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
            conn.commit()
            flash('Registered successfully.', 'success')  # ✅ success = green
            return redirect('/login')
        except:
            flash('Username already exists.', 'error')    # ✅ error = red
        finally:
            conn.close()
    return render_template('register.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = db.get_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (username, password)
        ).fetchone()
        conn.close()

        if user:
            session['user'] = user['id']
            session['role'] = user['role']
            return redirect('/')
        else:
            flash('Invalid username or password.', 'error')  # ✅ this triggers the message

    return render_template('login.html')

@bp.route('/logout')
def logout():
    session.clear()
    return redirect('/login')
