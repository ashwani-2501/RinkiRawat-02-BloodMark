from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Donation, DonorRegistration
import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24).hex()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/abdhe/OneDrive/Documents/GitHub/BloodMark/instance/bloodmark.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

model = tf.keras.models.load_model(r"C:\Users\abdhe\OneDrive\Documents\GitHub\BloodMark\model\model.h5")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

@app.route('/')
@app.route('/land')
def land():
    return render_template('land.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('land'))
        else:
            flash('Invalid username or password.')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            flash('Username or email already exists.')
            return redirect(url_for('login'))
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/detection', methods=['GET', 'POST'])
@login_required
def detection():
    if request.method == 'POST':
        if 'fingerprint' not in request.files:
            flash('No file uploaded.')
            return redirect(url_for('detection'))
        file = request.files['fingerprint']
        if file.filename == '':
            flash('No file selected.')
            return redirect(url_for('detection'))
        if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            flash('Invalid file type. Use PNG or JPG.')
            return redirect(url_for('detection'))
        img_path = os.path.join('static/uploads', file.filename)
        file.save(img_path)
        img = load_img(img_path, target_size=(64, 64))
        img_array = img_to_array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        class_names = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        prediction = model.predict(img_array)
        predicted_class = class_names[np.argmax(prediction)]
        new_donation = Donation(
            type='Detection',
            blood_type=predicted_class,
            location='Unknown',
            user_id=current_user.id
        )
        db.session.add(new_donation)
        db.session.commit()
        flash(f'Predicted blood group: {predicted_class}')
        return redirect(url_for('land'))
    return render_template('detection.html')

@app.route('/donation/volunteer', methods=['POST'])
@login_required
def donation_volunteer():
    name = request.form['name']
    phone = request.form['phone']
    available_days = request.form['available_days']
    new_donation = Donation(
        type='Volunteer',
        name=name,
        phone=phone,
        available_days=available_days,
        user_id=current_user.id
    )
    db.session.add(new_donation)
    db.session.commit()
    flash('Volunteer registration successful!')
    return redirect(url_for('donation'))

@app.route('/donation/donor', methods=['POST'])
@login_required
def donation_donor():
    location = request.form['location']
    donors = request.form['donors']
    donation_date = request.form['donation_date']
    availability = request.form['availability']
    new_donation = Donation(
        type='Donor',
        location=location,
        donors=donors,
        donation_date=donation_date,
        availability=availability,
        user_id=current_user.id
    )
    db.session.add(new_donation)
    db.session.commit()
    flash('Donor registration successful!')
    return redirect(url_for('donation'))

@app.route('/donation/needy', methods=['POST'])
@login_required
def donation_needy():
    patient_name = request.form['patient_name']
    blood_type = request.form['blood_type']
    location = request.form['location']
    new_donation = Donation(
        type='Needy',
        patient_name=patient_name,
        blood_type=blood_type,
        location=location,
        user_id=current_user.id
    )
    db.session.add(new_donation)
    db.session.commit()
    flash('Blood request submitted successfully!')
    return redirect(url_for('donation'))

@app.route('/donation')
@login_required
def donation():
    return render_template('donation.html')

@app.route('/submit_registration', methods=['GET', 'POST'])
@login_required
def submit_registration():
    if request.method == 'POST':
        full_name = request.form['fullName']
        dob = request.form['dob']
        gender = request.form['gender']
        blood_group = request.form['bloodGroup']
        weight = request.form['weight']
        contact = request.form['contact']
        email = request.form['email']
        address = request.form['address']
        recent_donation = request.form['recentDonation']
        medical_conditions = request.form.get('medicalConditions', '')
        consent = 'consent' in request.form
        if not consent:
            flash('You must provide consent to register.')
            return redirect(url_for('submit_registration'))
        new_registration = DonorRegistration(
            full_name=full_name,
            dob=dob,
            gender=gender,
            blood_group=blood_group,
            weight=weight,
            contact=contact,
            email=email,
            address=address,
            recent_donation=recent_donation,
            medical_conditions=medical_conditions,
            consent=consent,
            user_id=current_user.id
        )
        db.session.add(new_registration)
        db.session.commit()
        flash('Blood donation registration successful!')
        return redirect(url_for('land'))
    return render_template('form.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('land'))

if __name__ == '__main__':
    app.run(debug=True)