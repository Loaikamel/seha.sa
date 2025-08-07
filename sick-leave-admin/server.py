from flask import Flask, request, jsonify, send_from_directory
import json

app = Flask(__name__)

DATA_FILE = 'data.json'

@app.route('/')
def home():
    return send_from_directory('.', 'admin.html')

@app.route('/save', methods=['POST'])
def save():
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
def get_data():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return jsonify(data)

@app.route('/search')
def search():
    service_code = request.args.get('code')
    id_number = request.args.get('id')

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for record in data:
        if record['service_code'] == service_code and record['id_number'] == id_number:
            return jsonify(record)

    return "Not Found", 404


if __name__ == '__main__':
    app.run(debug=True)
