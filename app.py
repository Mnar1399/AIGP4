from flask import Flask, render_template, request, session
from analyze_idea import analyze_key_phrases, analyze_game_idea, analyze_project_cost
from task_utils import analyze_animation_suggestions, generate_character_images, suggest_gameplay_code
from flask import Flask, render_template, request, redirect, url_for
from flask_mail import Mail, Message
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import os
from analyze_idea import analyze_key_phrases, analyze_game_idea, analyze_project_cost
import requests
import random, re
from flask import Flask, send_from_directory, request, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from PIL import Image, ImageDraw
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import os

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json

# قراءة المفاتيح من ملف config.json
with open('config.json') as f:
    config = json.load(f)

# تعيين المفاتيح من الملف
openai_key = config["openai_key"]
text_analytics_key = config["text_analytics_key"]
openai_endpoint = config["openai_endpoint"]  # تأكد من أن المفتاح هنا هو "openai_endpoint" كما هو في config.json

# الآن يمكنك استخدام هذه المفاتيح في الكود
print(openai_key)  # فقط للتأكد من أن المفاتيح تم قراءتها بشكل صحيح



app = Flask(__name__)
app.secret_key = "supersecretkey"  # Essential for session handling


app = Flask(__name__)
app.secret_key = 'your_secret_key'


# قاعدة بيانات بسيطة لتخزين المستخدمين
users_db = {}
verification_codes = {}

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "your_email@gmail.com"
EMAIL_PASSWORD = "your_app_password"  # كلمة مرور التطبيق





@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    idea = data.get('idea', '')
    engine = data.get('engine', '')

    if not idea or not engine:
        return jsonify({"error": "Idea and engine are required fields."}), 400

    # Analyze the idea using OpenAI
    game_analysis = analyze_game_idea(idea)
    
    # Map tasks based on engine
    task_mapping = {
        "unity": "Create a Unity project, import assets, configure scenes, write C# scripts.",
        "unreal": "Set up Unreal Engine project, import models, create blueprints, configure materials."
    }
    tasks = task_mapping.get(engine.lower(), "General setup tasks for game development.")
    
    # Generate suggestions dynamically
    suggestions = f"Use {engine.capitalize()} for its strengths, such as high-quality rendering and performance optimization."

    return jsonify({
        "ideaAnalysis": game_analysis.get("choices", [{}])[0].get("message", {}).get("content", ""),
        "tasks": tasks,
        "suggestions": suggestions
    })



# صفحة تحليل فكرة اللعبة
@app.route('/', methods=['GET', 'POST'])
def home():
    game_name = None
    idea_summary = None
    requirements = []
    tasks = []
    selected_engine = 'unity'  # Unity كمحرك افتراضي

    if request.method == 'POST':
        game_idea = request.form['idea']
        selected_engine = request.form.get('engine', 'unity')

        # اسم اللعبة
        game_name = game_idea.strip()

        try:
            # استخدام Azure OpenAI للحصول على فكرة اللعبة
            openai_response = analyze_game_idea(game_name, openai_endpoint, openai_key)
            if "choices" in openai_response:
                idea_summary = openai_response["choices"][0]["message"]["content"]
            else:
                idea_summary = "Error generating game idea. Please try again."
        except Exception as e:
            print(f"Error communicating with OpenAI: {str(e)}")
            idea_summary = "Failed to generate game idea due to an error."

        # تخزين اسم اللعبة في جلسة المستخدم
        session['game_name'] = game_name
        session['idea_summary'] = idea_summary

        # أشياء يحتاجها المشروع
        requirements = [
            "High-quality assets for characters and environments.",
            "Game engine configurations for optimal performance.",
            "Sound effects and background music."
        ]

        # المهام (بناءً على المحرك)
        if selected_engine == "unity":
            tasks = [
                "Set up a Unity project and configure scenes.",
                "Program player movement using C#.",
                "Design animations and integrate them into the Animator.",
                "Add collision detection and implement physics."
            ]
        elif selected_engine == "unreal":
            tasks = [
                "Set up an Unreal Engine project and configure blueprints.",
                "Design character interactions and animations.",
                "Optimize rendering for high-quality visuals.",
                "Add sound effects and dynamic lighting."
            ]
        elif selected_engine == "godot":
            tasks = [
                "Set up a Godot project and configure nodes.",
                "Design interactive levels and player controls.",
                "Implement animations using the AnimationPlayer.",
                "Integrate audio and particle effects."
            ]
    
    return render_template(
        'home.html',
        game_name=game_name,
        idea_summary=idea_summary,
        requirements=requirements,
        tasks=tasks,
        selected_engine=selected_engine
    )


# صفحة الرسم (Draw)
@app.route('/draw', methods=['GET', 'POST'])
def draw():
    return render_template('draw.html')



# Project cost analysis page
@app.route('/cost', methods=['GET', 'POST'])
def cost():
    cost_analysis_result = None
    if request.method == 'POST':
        project_details = request.form['project_details']
        cost_analysis_result = analyze_project_cost(project_details, openai_endpoint, openai_key)

    return render_template('cost.html', cost_analysis=cost_analysis_result)

 

@app.route('/animation', methods=['GET', 'POST'])
def animation():
    game_name = session.get('game_name', '')
    idea_summary = session.get('idea_summary', '')

    # طباعة البيانات للتأكد من وجودها
    print(f"Game Name: {game_name}")
    print(f"Idea Summary: {idea_summary}")
    if not game_name or not idea_summary:
        return "No game idea available. Please submit a game idea first.", 400

    if request.method == 'POST':
        # تحليل وصف اللعبة لتحديد العناصر
        print("Generating pixel art based on idea summary...")
        
        # توليد الشخصية
        character_image_path = generate_pixel_art_character()
        
        # توليد الخريطة
        map_image_path = generate_pixel_art_map()

        return render_template('animation.html', 
                               description=idea_summary, 
                               character_image=character_image_path, 
                               map_image=map_image_path)

    # إذا لم يكن هناك طلب POST، عرض الصفحة بدون بيانات
    return render_template('animation.html', description=None, character_image=None, map_image=None)

def generate_pixel_art_character(image_size=64, pixel_size=8):
    """Generate a pixel art character and save it."""
    width, height = image_size, image_size
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)

    for x in range(0, width, pixel_size):
        for y in range(0, height, pixel_size):
            if random.choice([True, False]):
                color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                draw.rectangle([x, y, x + pixel_size, y + pixel_size], fill=color)

    path = "static/pixel_art_character.png"
    img.save(path)
    print(f"Character saved at {path}")
    return path

def generate_pixel_art_map(image_size=128, pixel_size=16):
    """Generate a pixel art map and save it."""
    width, height = image_size, image_size
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)

    colors = {
        "grass": (34, 139, 34),
        "water": (30, 144, 255),
        "dirt": (139, 69, 19)
    }

    for x in range(0, width, pixel_size):
        for y in range(0, height, pixel_size):
            element = random.choice(list(colors.keys()))
            draw.rectangle([x, y, x + pixel_size, y + pixel_size], fill=colors[element])

    path = "static/pixel_art_map.png"
    img.save(path)
    print(f"Map saved at {path}")
    return path

# Feedback page route
@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        # Handle the feedback logic (e.g., save to database, send email, etc.)
        print(f"Feedback received from {name} ({email}): {message}")

        # Redirect to a thank you page or display a success message
        return redirect(url_for('thank_you'))

    return render_template('feedback.html')

# Thank you page route
@app.route('/thank-you')
def thank_you():
    return render_template('thank_you.html')


# AIGP page route
@app.route('/aigp', methods=['GET'])
def aigp():
    return render_template('aigp.html')

# task page route
@app.route('/task', methods=['GET'])
def task():
    return render_template('task.html')





# إعداد قاعدة البيانات
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# نموذج المستخدم
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    

# إنشاء قاعدة البيانات
with app.app_context():
    db.create_all()

# صفحة التسجيل
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        
        # Check if the email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('This email is already registered. Please log in or use a different email.', 'danger')
            return redirect(url_for('register'))
        
        # Save the new user in the database
        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

# صفحة تسجيل الدخول
@app.route('/login', methods=['GET', 'POST'])
def login():
    error_message = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Check if the email exists in the database
        user = User.query.filter_by(email=email).first()
        if user:
            # Check if the password is correct
            if bcrypt.check_password_hash(user.password, password):
                session['user_id'] = user.id
                flash('Login successful.', 'success')
                return redirect(url_for('profile'))
            else:
                error_message = "Incorrect password. Please try again."
        else:
            error_message = "Email address not found. Please check or create a new account."

    return render_template('login.html', error_message=error_message)

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('You need to log in to access your profile.', 'danger')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    return render_template('profile.html', user=user)

# تسجيل الخروج
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('تم تسجيل الخروج بنجاح.', 'success')
    return redirect(url_for('login'))


from flask import session

@app.route('/dashboard')
def dashboard():
    # Check if the user has already seen the tour
    if not session.get('tour_seen', False):
        session['tour_seen'] = True  # Mark the tour as seen
        show_tour = True
    else:
        show_tour = False

    return render_template('dashboard.html', show_tour=show_tour)



@app.route('/details/<engine>', methods=['GET'])
def view_details(engine):
    engine_info = {
        "unity": {
            "name": "Unity Game Engine",
            "description": "Unity is a cross-platform game engine widely used for creating 2D and 3D games.",
            "how_to_use": [
                "Download and install Unity Hub.",
                "Create a new project and select 2D or 3D template.",
                "Learn the basics of C# scripting for player controls.",
                "Design levels using Unity's scene editor.",
                "Add animations using the Animator tool."
            ]
        },
        "unreal": {
            "name": "Unreal Engine",
            "description": "Unreal Engine is a high-performance engine widely used for AAA games and real-time rendering.",
            "how_to_use": [
                "Download and install Unreal Engine from Epic Games.",
                "Create a new project using Blueprints or C++.",
                "Learn level design and lighting techniques.",
                "Optimize performance using the profiling tools.",
                "Add interactive elements using Blueprints."
            ]
        },
        "godot": {
            "name": "Godot Engine",
            "description": "Godot Engine is an open-source game engine ideal for 2D and 3D game development.",
            "how_to_use": [
                "Download and install Godot Engine.",
                "Create a new project and configure nodes.",
                "Use GDScript for scripting game logic.",
                "Design levels and UI with the built-in tools.",
                "Add animations using the AnimationPlayer."
            ]
        }
    }
    engine_data = engine_info.get(engine.lower(), {})
    return render_template('details.html', engine_data=engine_data, engine=engine)

@app.route('/ask_bot', methods=['POST'])
def ask_bot():
    data = request.json
    question = data.get('question', '').strip()
    engine = data.get('engine', 'Unnamed Game').strip()  # اسم المحرك
    # استرجاع اسم اللعبة من الجلسة
    game_name = session.get('game_name', 'Unnamed Game')

    if not question or not engine or not game_name:
        return jsonify({"error": "Please provide a question and a game engine."}), 400
    

    headers = {
        "Content-Type": "application/json",
        "api-key": openai_key
    }
    # صياغة الرسالة للإرسال إلى OpenAI
    openai_request = {
        "messages": [
            {"role": "system", "content": f"You are a helpful assistant specialized in the {engine} game engine.The game name is '{game_name}'. Answer questions concisely and provide helpful guidance for developers."},
            {"role": "user", "content": question}
        ],
        "max_tokens": 300,
        "temperature": 0.7
    }

            

    # إرسال الطلب إلى Azure OpenAI
    try:
        headers = {
            "Content-Type": "application/json",
            "api-key": openai_key
        }
        url = f"{openai_endpoint}/openai/deployments/gpt-35-turbo/chat/completions?api-version=2024-08-01-preview"
        response = requests.post(url, headers=headers, json=openai_request)
        response_data = response.json()

        # التحقق من الرد من OpenAI
        if response.status_code == 200 and "choices" in response_data and len(response_data["choices"]) > 0:
            reply = response_data["choices"][0]["message"]["content"]
        elif "error" in response_data:
            reply = f"Error from OpenAI: {response_data['error'].get('message', 'Unknown error.')}"
        else:
            reply = "I'm sorry, I couldn't generate a response. Please try again."

    except Exception as e:
        reply = f"Error communicating with OpenAI: {str(e)}"
    
    return jsonify({"reply": reply})



if __name__ == '__main__':
    app.run(debug=True, port=5001)

