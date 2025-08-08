from flask import Flask, request, jsonify, send_from_directory, session, redirect, url_for
import json
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = os.urandom(24)

DATA_FILE = 'data.json'

# بيانات المسؤولين (يمكن تخزينها في قاعدة بيانات في الإنتاج)
ADMIN_CREDENTIALS = {
    'admin': 'admin123',  # اسم المستخدم: كلمة المرور
    'manager': 'manager123'
}

def admin_required(f):
    """ديكوريتر للتحقق من صلاحيات المسؤول"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_type' not in session or session['user_type'] != 'admin':
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route("/")
def home():
    """الصفحة الرئيسية - تعرض صفحة الاستعلام دائمًا"""
    return send_from_directory(".", "index.html")




@app.route('/login')
def login():
    """صفحة تسجيل الدخول"""
    return send_from_directory('.', 'login.html')

@app.route("/login", methods=["POST"])
def login_post():
    """معالجة تسجيل الدخول"""
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    
    if username in ADMIN_CREDENTIALS and ADMIN_CREDENTIALS[username] == password:
        session["user_type"] = "admin"
        session["username"] = username
        return jsonify({"success": True, "redirect": "/admin"}) # توجيه مباشر إلى /admin
    else:
        return jsonify({"success": False, "message": "اسم المستخدم أو كلمة المرور غير صحيحة"})



@app.route('/logout')
def logout():
    """تسجيل الخروج"""
    session.clear()
    return redirect(url_for('home'))

@app.route('/admin')
@admin_required
def admin_panel():
    """لوحة تحكم المسؤول"""
    return send_from_directory('.', 'admin.html')

@app.route('/save', methods=['POST'])
@admin_required
def save():
    """حفظ البيانات - للمسؤولين فقط"""
    new_data = request.get_json()

    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except:
        data = []

    data.append(new_data)

    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return "✅ تم حفظ البيانات بنجاح!"

@app.route('/data', methods=['GET'])
@admin_required
def get_data():
    """عرض جميع البيانات - للمسؤولين فقط"""
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data)
    except:
        return jsonify([])

@app.route('/search')
def search():
    """البحث عن البيانات - متاح للجميع"""
    service_code = request.args.get('code')
    id_number = request.args.get('id')

    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except:
        return "Not Found", 404

    for record in data:
        if record['service_code'] == service_code and record['id_number'] == id_number:
            return jsonify(record)

    return "Not Found", 404

@app.route('/static/<path:filename>')
def static_files(filename):
    """تقديم الملفات الثابتة"""
    return send_from_directory('static', filename)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)


