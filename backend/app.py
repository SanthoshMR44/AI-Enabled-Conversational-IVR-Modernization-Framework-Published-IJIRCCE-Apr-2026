import os
from flask import Flask, render_template, send_from_directory, redirect, url_for
from database import init_db

# Initialize database
init_db()

# Seed default mock data for analytics if empty
from seed_data import seed_analytics
seed_analytics()

app = Flask(__name__, 
            static_folder=os.path.join(os.path.dirname(__file__), 'static'),
            template_folder=os.path.join(os.path.dirname(__file__), 'templates'))

app.secret_key = 'ivr_modernization_secret_key'

# Register Blueprints
from routes.auth import auth_bp
from routes.ivr import ivr_bp
from routes.flow import flow_bp
from routes.intent import intent_bp
from routes.kb import kb_bp
from routes.reports import reports_bp
from routes.admin import admin_bp

app.register_blueprint(auth_bp)
app.register_blueprint(ivr_bp)
app.register_blueprint(flow_bp)
app.register_blueprint(intent_bp)
app.register_blueprint(kb_bp)
app.register_blueprint(reports_bp)
app.register_blueprint(admin_bp)

# HTML Page Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/signup')
def signup_page():
    return render_template('signup.html')

@app.route('/dashboard')
def dashboard_page():
    return render_template('dashboard.html')

@app.route('/designer')
def designer_page():
    return render_template('designer.html')

@app.route('/simulator')
def simulator_page():
    return render_template('simulator.html')

@app.route('/kb')
def kb_page():
    return render_template('kb.html')

@app.route('/admin')
def admin_page():
    return render_template('admin.html')

if __name__ == '__main__':
    app.run(port=5000, debug=True)
