from flask import Blueprint, render_template, request, redirect, session, g
import db

bp = Blueprint('assets', __name__)

@bp.route('/')
def dashboard():
    if not session.get('user'):
        return redirect('/login')
    conn = db.get_connection()
    assets = conn.execute("""
        SELECT assets.id, assets.name, assets.type, users.username, assets.owner_id
        FROM assets JOIN users ON assets.owner_id = users.id
    """).fetchall()
    conn.close()
    return render_template('dashboard.html', assets=assets)

@bp.route('/create', methods=['GET', 'POST'])
def create_asset():
    if not session.get('user'):
        return redirect('/login')
    if request.method == 'POST':
        name = request.form['name']
        type_ = request.form['type']
        conn = db.get_connection()
        conn.execute("INSERT INTO assets (name, type, owner_id) VALUES (?, ?, ?)", (name, type_, session['user']))
        conn.commit()
        conn.close()
        return redirect('/')
    return render_template('asset_form.html', asset=None)

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_asset(id):
    if not session.get('user'):
        return redirect('/login')
    conn = db.get_connection()
    asset = conn.execute("SELECT * FROM assets WHERE id = ?", (id,)).fetchone()

    if not asset or asset['owner_id'] != session['user']:
        conn.close()
        return redirect('/')

    if request.method == 'POST':
        name = request.form['name']
        type_ = request.form['type']
        conn.execute("UPDATE assets SET name = ?, type = ? WHERE id = ?", (name, type_, id))
        conn.commit()
        conn.close()
        return redirect('/')

    conn.close()
    return render_template('asset_form.html', asset=asset)

@bp.route('/delete/<int:id>')
def delete_asset(id):
    if session.get('role') != 'admin':
        return redirect('/')
    conn = db.get_connection()
    conn.execute("DELETE FROM assets WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect('/')
