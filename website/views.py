from flask import Blueprint, render_template, request, flash, jsonify, session, redirect, url_for
from flask_login import login_required, current_user
from .models import Complaint, Response
from datetime import datetime
from website import db
import json

MAX_MESSAGES_PER_DAY = 2
views = Blueprint('views', __name__)

# Langauges
@views.before_app_request
def detect_lang():
    lang = request.args.get('lang') or session.get('lang')
    if lang in ['ar', 'en']:
        session['lang'] = lang
    elif 'lang' not in session:
        session['lang'] = 'en'

# Home for students:
@views.route('/', methods=["GET", 'POST'])
@login_required
def home():
    if current_user.user_type != 'student':
        return redirect(url_for('admin.dashboard'))

    lang = session.get('lang', 'en')

    complaints = Complaint.query.filter_by(student_id=current_user.id).all()
    today = datetime.today().date()
    complaints_today = Complaint.query.filter_by(student_id=current_user.id).filter(db.func.date(Complaint.date_created) == today).all()
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('note')
        if len(complaints_today) >= MAX_MESSAGES_PER_DAY:
            flash('لقد وصلت إلى الحد الأقصى للشكاوى لهذا اليوم' if lang == 'ar' else 'You have reached the daily limit of complaints.', category='error')
################################################################################################################################################################################################3
        elif not title or len(title.strip()) < 3 or not title:
            flash('يرجى ملء جميع الحقول بشكل صحيح' if lang == 'ar' else 'Please fill all fields correctly', category='error')
################################################################################################################################################################################################
        elif not description or len(description.strip()) < 3 or not description:
            flash('يجب ان يتجاوز ٣ احرف' if lang == 'ar' else 'Must be more than 3 characters', category='error')
        else:
            new_complaint = Complaint(title=title.strip(), description=description.strip(), student_id=current_user.id)
            db.session.add(new_complaint)
            db.session.commit()
            flash('تم إرسال الشكوى بنجاح، سيتم مراجعتها خلال ٣ أيام' if lang == 'ar' else 'Complaint submitted successfully, it will be reviewed within 3 days', category='success')
        return redirect(url_for('views.home'))
    return render_template("home.html", user=current_user, complaints=complaints, lang=lang)

#delete_complaint
@views.route('/delete-complaint', methods=['POST'])
@login_required
def delete_complaint():
    if current_user.user_type != 'student':
        return jsonify({'success': False}), 403

    data = json.loads(request.data)
    complaint_id = data.get('complaintId')
    complaint = Complaint.query.get(complaint_id)
    if complaint:
        if complaint.student_id == current_user.id:
            db.session.delete(complaint)
            db.session.commit()
            return jsonify({'success': True})
    return jsonify({'success': False}), 403

# track_complaints
@views.route('/track-complaints')
def track_complaints():
    complaint_id = request.args.get('complaint_id')  # URL (e.g, complaint_id=1) 
    complaint = Complaint.query.get(complaint_id)    # from database
    if complaint:                                    # display complaint if it exist
        return render_template('track_complaints.html', complaint=complaint, user=current_user)
    # dosn't exist
    user_type = None
    if current_user.is_authenticated:
        user_type = current_user.user_type
    return render_template('track_complaints.html', complaint=complaint, user=current_user, user_type=user_type)

# display complaints
@views.context_processor
def inject_complaints():
    complaints = []
    if current_user.is_authenticated and current_user.user_type == 'student':
        complaints = Complaint.query.filter_by(student_id=current_user.id).order_by(Complaint.date_created.desc()).all()
    lang = session.get('lang', 'en')
    return dict(complaints=complaints, lang=lang)

# complaint_data
@views.route('/complaint-data/<int:complaint_id>')
@login_required
def complaint_data(complaint_id):
    lang = session.get('lang', 'en')
    complaint = Complaint.query.get_or_404(complaint_id)
    if complaint.student_id != current_user.id:
        return jsonify({'error': 'Access denied' if lang == 'en' else 'غير مصرح لك'}), 403

    responses = [{
        'text': r.response_text,
        'date': r.date_created.strftime('%Y-%m-%d %H:%M')
    } for r in complaint.responses]
    return jsonify({
        'title': complaint.title,
        'description': complaint.description,
        'date': complaint.date_created.strftime('%Y-%m-%d %H:%M'),
        'responses': responses,
        'rating': complaint.rating

    })

@views.route('/submit-rating', methods=['POST'])
@login_required
def submit_rating():
    data = request.get_json()
    response_id = data.get('responseId')
    rating = data.get('rating')

    if not response_id or not rating:
        return jsonify({'success': False, 'message': 'Invalid data'}), 400

    try:
        response = Response.query.get(response_id)
        if response:
            response.rating = rating
            db.session.commit()
            return jsonify({'success': True})
    except NoResultFound:
        return jsonify({'success': False, 'message': 'Response not found'}), 404



###################################
admin = Blueprint('admin', __name__)

@admin.route('/reply-complaint/<complaint_id>', methods=['POST'])
@login_required
def reply_complaint(complaint_id):
    complaint = Complaint.query.get_or_404(complaint_id) # check if complaint is exist
    if current_user.user_type != 'admin':
        return redirect(url_for('views.home'))  # (check) only admins
    response_text = request.form.get('response')
    if response_text:
        response = Response(
            response_text=response_text, 
            complaint_id=complaint.id, 
            admin_id=current_user.id,
        )
        db.session.add(response)
        db.session.commit()
    return redirect(url_for('views.track_complaints', complaint_id=complaint.id))

# Admin dashboard
@admin.route('/dashboard')
@login_required
def dashboard():
    if current_user.user_type != 'admin':
        flash("Access denied", category="error")
        return redirect(url_for('views.home'))

    complaints = Complaint.query.order_by(Complaint.date_created.desc()).all()
    lang = session.get('lang', 'en')
    return render_template('admin/adminDashboard.html', complaints=complaints, user=current_user, lang=lang)
