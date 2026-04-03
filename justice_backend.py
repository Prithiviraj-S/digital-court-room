from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import sqlite3
import json
from datetime import datetime
import os

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# Database setup
DATABASE = 'justice_system.db'

def get_db():
    conn = sqlite3.connect(DATABASE, timeout=10.0)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if not os.path.exists(DATABASE):
        try:
            conn = get_db()
            cursor = conn.cursor()
            
            # Create cases table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    case_id TEXT UNIQUE NOT NULL,
                    case_type TEXT NOT NULL,
                    status TEXT DEFAULT 'PENDING',
                    plaintiff TEXT NOT NULL,
                    defendant TEXT NOT NULL,
                    description TEXT,
                    date_filed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    date_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create judgments table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS judgments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    case_id TEXT NOT NULL,
                    judge_name TEXT NOT NULL,
                    verdict TEXT NOT NULL,
                    verdict_details TEXT,
                    date_issued TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (case_id) REFERENCES cases(case_id)
                )
            ''')
            
            # Create evidence table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS evidence (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    case_id TEXT NOT NULL,
                    evidence_type TEXT NOT NULL,
                    description TEXT,
                    date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (case_id) REFERENCES cases(case_id)
                )
            ''')
            
            conn.commit()
            conn.close()
            print("✓ Database initialized successfully")
        except Exception as e:
            print(f"✗ Error initializing database: {e}")

@app.route('/')
def index():
    return send_file('portfolio.html')

@app.route('/api/case/submit', methods=['POST'])
def submit_case():
    try:
        data = request.json
        conn = get_db()
        cursor = conn.cursor()
        
        case_id = f"CASE-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        cursor.execute('''
            INSERT INTO cases (case_id, case_type, plaintiff, defendant, description, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (case_id, data['case_type'], data['plaintiff'], data['defendant'], data['description'], 'PENDING'))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Case submitted successfully',
            'case_id': case_id,
            'status': 'PENDING'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/case/<case_id>', methods=['GET'])
def get_case(case_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Get case details
        cursor.execute('SELECT * FROM cases WHERE case_id = ?', (case_id,))
        case = cursor.fetchone()
        
        if not case:
            return jsonify({'success': False, 'error': 'Case not found'}), 404
        
        # Get judgments
        cursor.execute('SELECT * FROM judgments WHERE case_id = ? ORDER BY date_issued DESC', (case_id,))
        judgments = cursor.fetchall()
        
        # Get evidence
        cursor.execute('SELECT * FROM evidence WHERE case_id = ? ORDER BY date_added DESC', (case_id,))
        evidence = cursor.fetchall()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'case': dict(case),
            'judgments': [dict(j) for j in judgments],
            'evidence': [dict(e) for e in evidence]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/judgment/submit', methods=['POST'])
def submit_judgment():
    try:
        data = request.json
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO judgments (case_id, judge_name, verdict, verdict_details)
            VALUES (?, ?, ?, ?)
        ''', (data['case_id'], data['judge_name'], data['verdict'], data['verdict_details']))
        
        # Update case status
        cursor.execute('UPDATE cases SET status = ?, date_updated = CURRENT_TIMESTAMP WHERE case_id = ?',
                    (data['verdict'], data['case_id']))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Judgment submitted successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/evidence/submit', methods=['POST'])
def submit_evidence():
    try:
        data = request.json
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO evidence (case_id, evidence_type, description)
            VALUES (?, ?, ?)
        ''', (data['case_id'], data['evidence_type'], data['description']))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Evidence submitted successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/cases', methods=['GET'])
def get_all_cases():
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM cases ORDER BY date_filed DESC')
        cases = cursor.fetchall()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'cases': [dict(c) for c in cases]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
