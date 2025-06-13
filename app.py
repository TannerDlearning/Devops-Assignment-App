from flask import Flask, render_template, request, redirect, session, g
import db
import auth
import assets

app = Flask(__name__)
app.secret_key = 'super-secret-key'

# Register routes from auth.py and assets.py
app.register_blueprint(auth.bp)
app.register_blueprint(assets.bp)

@app.before_request
def load_logged_in_user():
    g.user = session.get('user')
    g.role = session.get('role')

if __name__ == '__main__':
    db.init_db()
    app.run(debug=True)
