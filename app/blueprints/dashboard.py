from flask import Blueprint, render_template,session

dashboard = Blueprint('dashboard', __name__)

@dashboard.route('/dashboard')
def dashboard_page():
    return render_template('dashboard.html')