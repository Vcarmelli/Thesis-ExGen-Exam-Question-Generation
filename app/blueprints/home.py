from flask import Blueprint, render_template, session
from ..schema import QuestionSet, Question
from .. import db
from sqlalchemy import func
from datetime import datetime
import pytz

home = Blueprint('home', __name__)

@home.route('/home')
def home_page():
    session.clear()
    
    # Get all question sets
    question_sets = QuestionSet.query.order_by(QuestionSet.created_at.desc()).limit(3).all()
    
    # Get recent exams (last 3)
    recent_exams = QuestionSet.query.order_by(QuestionSet.created_at.desc()).limit(3).all()
    
    # Get counts for each Bloom's level
    counts = {}
    bloom_levels = ['remember', 'understand', 'apply', 'analyze', 'evaluate', 'create']
    
    for level in bloom_levels:
        count = Question.query.filter_by(bloom=level).count()
        counts[level] = count
    
    # Convert timestamps to Philippine time (UTC+8)
    ph_timezone = pytz.timezone('Asia/Manila')
    
    for exam in recent_exams:
        if exam.created_at.tzinfo is None:
            # If timestamp is naive, assume it's UTC
            utc_time = pytz.utc.localize(exam.created_at)
            exam.created_at = utc_time.astimezone(ph_timezone)
        else:
            exam.created_at = exam.created_at.astimezone(ph_timezone)
    
    return render_template('home.html',
                          question_sets=question_sets,
                          recent_exams=recent_exams,
                          counts=counts)