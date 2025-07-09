from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from .models import Complaint, Response
from website import db

admin = Blueprint('admin', __name__, url_prefix='/admin')

@admin.route('/dashboard')
@login_required
def dashboard():
    if current_user.user_type != 'admin':
        flash("Access denied", category="error")
        return redirect(url_for('views.home'))

    complaints = Complaint.query.order_by(Complaint.date_created.desc()).all()
    lang = session.get('lang', 'en')
    return render_template('admin/adminDashboard.html', complaints=complaints, user=current_user, lang=lang)

@admin.route('/respond/<int:complaint_id>', methods=['GET', 'POST'])
@login_required
def respond_to_complaint(complaint_id):
    if current_user.user_type != 'admin':
        flash("Access denied", category="error")
        return redirect(url_for('views.home'))

    complaint = Complaint.query.get_or_404(complaint_id)

    if request.method == 'POST':
        response_text = request.form.get('response')
        if len(response_text) < 4:
            flash('Response is too short', category='error')
        else:
            new_response = Response(
                response_text=response_text,
                complaint_id=complaint.id,
                admin_id=current_user.id
            )
            db.session.add(new_response)
            db.session.commit()
            flash('Response sent successfully', category='success')
            return redirect(url_for('admin.dashboard'))

    lang = session.get('lang', 'en')
    return render_template('admin/respond.html', complaint=complaint, lang=lang, user=current_user)

