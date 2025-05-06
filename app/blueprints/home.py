from flask import Blueprint, render_template, session
from ..schema import QuestionSet, Question, Keynote  # Add Keynote import
import pytz

home = Blueprint('home', __name__)

@home.route('/home')
def home_page():
    session.clear()
    
    # Get all question sets
    question_sets = QuestionSet.query.order_by(QuestionSet.created_at.desc()).limit(3).all()
    
    # Get recent exams (last 3)
    recent_exams = QuestionSet.query.order_by(QuestionSet.created_at.desc()).limit(3).all()
    
    # Get keynote sets and recent keynotes
    keynote_sets = Keynote.query.order_by(Keynote.created_at.desc()).limit(3).all()
    recent_keynotes = Keynote.query.order_by(Keynote.created_at.desc()).limit(3).all()
    
    # Get counts for each Bloom's level
    counts = {}
    bloom_levels = ['remember', 'understand', 'apply', 'analyze', 'evaluate', 'create']
    
    for level in bloom_levels:
        count = Question.query.filter_by(bloom=level).count()
        counts[level] = count
    
    # Convert timestamps to Philippine time (UTC+8)
    ph_timezone = pytz.timezone('Asia/Manila')
    
    # Convert exam timestamps
    for exam in recent_exams:
        if exam.created_at and exam.created_at.tzinfo is None:
            utc_time = pytz.utc.localize(exam.created_at)
            exam.created_at = utc_time.astimezone(ph_timezone)
    
    # Convert keynote timestamps
    for keynote in recent_keynotes:
        if keynote.created_at and keynote.created_at.tzinfo is None:
            utc_time = pytz.utc.localize(keynote.created_at)
            keynote.created_at = utc_time.astimezone(ph_timezone)
    
    return render_template('home.html',
                         question_sets=question_sets,
                         keynote_sets=keynote_sets,
                         recent_exams=recent_exams,
                         recent_keynotes=recent_keynotes,
                         counts=counts)