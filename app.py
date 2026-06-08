from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "icclub123"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///club.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ---------------- MODELS ----------------
class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    department = db.Column(db.String(50))
    role = db.Column(db.String(100))
    year = db.Column(db.String(20))

class Update(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    content = db.Column(db.Text)

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)

with app.app_context():
    db.create_all()

# ---------------- ADMIN ----------------
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        if request.form.get('username') == ADMIN_USERNAME and request.form.get('password') == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect('/dashboard')
        flash("Invalid login")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect('/')

# ---------------- HOME ----------------
@app.route('/')
def index():
    return render_template('index.html',
        members=Member.query.all(),
        updates=Update.query.all(),
        activities=Activity.query.all()
    )

# ---------------- MEMBERS ----------------
@app.route('/members')
def members():
    return render_template('members.html', members=Member.query.all())

@app.route('/add_member', methods=['GET', 'POST'])
def add_member():
    if not session.get('admin'):
        return redirect('/login')

    if request.method == 'POST':
        name = request.form.get('name')
        department = request.form.get('department')
        role = request.form.get('role')
        year = request.form.get('year')

        if not name or not department or not role or not year:
            flash("All fields are required!")
            return redirect('/add_member')

        db.session.add(Member(
            name=name,
            department=department,
            role=role,
            year=year
        ))
        db.session.commit()

        return redirect('/members')

    return render_template('add_member.html')
# ---------------- REDIRECT ROUTE (ADD FIX) ----------------
@app.route('/add')
def add_redirect():
    return redirect('/add_member')

# ✅ FIXED: DELETE MEMBER (WAS MISSING)
@app.route('/delete_member/<int:id>')
def delete_member(id):
    if not session.get('admin'):
        return redirect('/login')

    member = Member.query.get(id)
    if member:
        db.session.delete(member)
        db.session.commit()

    return redirect('/members')

# ---------------- UPDATES ----------------
@app.route('/updates')
def updates():
    return render_template('updates.html', updates=Update.query.all())

@app.route('/add_update', methods=['GET','POST'])
def add_update():
    if not session.get('admin'):
        return redirect('/login')

    if request.method == 'POST':
        db.session.add(Update(
            title=request.form.get('title'),
            content=request.form.get('content')
        ))
        db.session.commit()
        return redirect('/updates')

    return render_template('add_update.html')

@app.route('/delete_update/<int:id>')
def delete_update(id):
    if not session.get('admin'):
        return redirect('/login')

    item = Update.query.get(id)
    if item:
        db.session.delete(item)
        db.session.commit()

    return redirect('/updates')

# ---------------- ACTIVITIES ----------------
@app.route('/activities')
def activities():
    return render_template('activities.html', activities=Activity.query.all())

@app.route('/add_activity', methods=['GET','POST'])
def add_activity():
    if not session.get('admin'):
        return redirect('/login')

    if request.method == 'POST':
        db.session.add(Activity(
            title=request.form.get('title'),
            description=request.form.get('description')
        ))
        db.session.commit()
        return redirect('/activities')

    return render_template('add_activity.html')

@app.route('/delete_activity/<int:id>')
def delete_activity(id):
    if not session.get('admin'):
        return redirect('/login')

    item = Activity.query.get(id)
    if item:
        db.session.delete(item)
        db.session.commit()

    return redirect('/activities')

# ---------------- DASHBOARD ----------------
@app.route('/dashboard')
def dashboard():
    if not session.get('admin'):
        return redirect('/login')

    return render_template('dashboard.html')

# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(debug=True, port=5002)