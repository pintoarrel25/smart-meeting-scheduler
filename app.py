from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from database import init_db
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Initialize the database
init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('smart_meeting_scheduler.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['username'] = user[1]
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        
        conn = sqlite3.connect('smart_meeting_scheduler.db')
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO users (username, password, email) VALUES (?, ?, ?)', 
                           (username, hashed_password, email))
            conn.commit()
            flash('Registration successful! Please login.')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username or email already exists')
        finally:
            conn.close()
    
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('smart_meeting_scheduler.db')
    cursor = conn.cursor()
    
    # Fetch completed meetings
    cursor.execute('SELECT title, start_time, end_time FROM meetings WHERE organizer_id = ? AND end_time < ?', 
                   (session['user_id'], datetime.now().isoformat()))
    completed_meetings = cursor.fetchall()
    
    # Fetch upcoming meetings
    cursor.execute('SELECT title, start_time, end_time FROM meetings WHERE organizer_id = ? AND start_time >= ?', 
                   (session['user_id'], datetime.now().isoformat()))
    upcoming_meetings = cursor.fetchall()
    
    # Fetch priority meetings (within 3 days)
    three_days_later = (datetime.now() + timedelta(days=3)).isoformat()
    cursor.execute('SELECT title, start_time, end_time FROM meetings WHERE organizer_id = ? AND start_time BETWEEN ? AND ?', 
                   (session['user_id'], datetime.now().isoformat(), three_days_later))
    priority_meetings = cursor.fetchall()
    
    conn.close()
    
    return render_template('dashboard.html', username=session['username'], 
                           completed_meetings=completed_meetings, 
                           upcoming_meetings=upcoming_meetings, 
                           priority_meetings=priority_meetings)

@app.route('/schedule', methods=['GET', 'POST'])
def schedule():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('smart_meeting_scheduler.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, username FROM users')
    users = cursor.fetchall()
    conn.close()
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        
        conn = sqlite3.connect('smart_meeting_scheduler.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO meetings (title, description, start_time, end_time, organizer_id) VALUES (?, ?, ?, ?, ?)', 
                       (title, description, start_time, end_time, session['user_id']))
        conn.commit()
        conn.close()
        
        flash('Meeting scheduled successfully!')
        return redirect(url_for('dashboard'))
    
    if request.method == 'GET':
        conn = sqlite3.connect('smart_meeting_scheduler.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, title, start_time, end_time FROM meetings WHERE organizer_id = ?', (session['user_id'],))
        meetings = cursor.fetchall()
        conn.close()
        return render_template('schedule.html', users=users, meetings=meetings)
    
    return render_template('schedule.html', users=users)

@app.route('/get_meetings')
def get_meetings():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('smart_meeting_scheduler.db')
    cursor = conn.cursor()
    cursor.execute('SELECT title, start_time, end_time FROM meetings WHERE organizer_id = ?', (session['user_id'],))
    meetings = cursor.fetchall()
    conn.close()
    
    events = []
    for meeting in meetings:
        events.append({
            'title': meeting[0],
            'start': meeting[1],
            'end': meeting[2]
        })
    
    return jsonify(events)

@app.route('/get_meeting/<int:meeting_id>')
def get_meeting(meeting_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('smart_meeting_scheduler.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, description, start_time, end_time FROM meetings WHERE id = ? AND organizer_id = ?', 
                   (meeting_id, session['user_id']))
    meeting = cursor.fetchone()
    conn.close()
    
    if meeting:
        return jsonify({
            'id': meeting[0],
            'title': meeting[1],
            'description': meeting[2],
            'start_time': meeting[3],
            'end_time': meeting[4]
        })
    else:
        return jsonify({'error': 'Meeting not found'}), 404

@app.route('/update_meeting/<int:meeting_id>', methods=['POST'])
def update_meeting(meeting_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    title = request.form['title']
    description = request.form['description']
    start_time = request.form['start_time']
    end_time = request.form['end_time']
    
    conn = sqlite3.connect('smart_meeting_scheduler.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE meetings SET title = ?, description = ?, start_time = ?, end_time = ? WHERE id = ? AND organizer_id = ?', 
                   (title, description, start_time, end_time, meeting_id, session['user_id']))
    conn.commit()
    conn.close()
    
    flash('Meeting updated successfully!')
    return redirect(url_for('dashboard'))

@app.route('/delete_meeting/<int:meeting_id>', methods=['POST'])
def delete_meeting(meeting_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('smart_meeting_scheduler.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM meetings WHERE id = ? AND organizer_id = ?', (meeting_id, session['user_id']))
    conn.commit()
    conn.close()
    
    flash('Meeting deleted successfully!')
    return redirect(url_for('dashboard'))

@app.route('/availability', methods=['GET', 'POST'])
def availability():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        
        conn = sqlite3.connect('smart_meeting_scheduler.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO availability (user_id, start_time, end_time) VALUES (?, ?, ?)', 
                       (session['user_id'], start_time, end_time))
        conn.commit()
        conn.close()
        
        flash('Availability added successfully!')
        return redirect(url_for('dashboard'))
    
    return render_template('availability.html')

def merge_intervals(intervals):
    intervals.sort(key=lambda x: x[0])
    merged = []
    for interval in intervals:
        if not merged or merged[-1][1] < interval[0]:
            merged.append(interval)
        else:
            merged[-1][1] = max(merged[-1][1], interval[1])
    return merged

def find_common_slots(availability):
    if not availability:
        return []
    
    common_slots = availability[0]
    for slots in availability[1:]:
        new_common_slots = []
        i, j = 0, 0
        while i < len(common_slots) and j < len(slots):
            start = max(common_slots[i][0], slots[j][0])
            end = min(common_slots[i][1], slots[j][1])
            if start < end:
                new_common_slots.append([start, end])
            if common_slots[i][1] < slots[j][1]:
                i += 1
            else:
                j += 1
        common_slots = new_common_slots
    return common_slots

@app.route('/suggest_slots', methods=['POST'])
def suggest_slots():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    participants = request.form.getlist('participants')
    
    conn = sqlite3.connect('smart_meeting_scheduler.db')
    cursor = conn.cursor()
    
    # Fetch availability of all participants
    availability = []
    for participant in participants:
        cursor.execute('SELECT start_time, end_time FROM availability WHERE user_id = ?', (participant,))
        slots = cursor.fetchall()
        slots = [[datetime.fromisoformat(slot[0]), datetime.fromisoformat(slot[1])] for slot in slots]
        availability.append(merge_intervals(slots))
    
    # Find common available slots
    common_slots = find_common_slots(availability)
    
    conn.close()
    
    return jsonify([[slot[0].isoformat(), slot[1].isoformat()] for slot in common_slots])

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
