import hashlib
from flask import Flask, request, jsonify, send_file, render_template_string
from firebase_admin import credentials, firestore, initialize_app
from PIL import Image, ImageDraw, ImageFont
import io
import random, string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

cred = credentials.Certificate('backend/cred.json')
initialize_app(cred)
db = firestore.client()

@app.route('/')
def home():
    with open('frontend/index.html', 'r', encoding='utf-8') as f:
        content = f.read()
    return render_template_string(content)

def generate_salt(length=8):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

def add_name_to_image(name, credential_id, project):
    img = Image.open('img/cret.jpg')
    draw = ImageDraw.Draw(img)

    name_font_size = 110
    name_font = ImageFont.truetype('ttf/GoogleSans-Bold.ttf', name_font_size)
    name_fill_color = (137, 128, 200)

    draw.text(
        (480, 605),
        name,
        font=name_font,
        fill=name_fill_color,
        stroke_width=2,
        stroke_fill=name_fill_color
    )

    second_line_text = f'Team member, {project}'
    second_line_font_size = int(name_font_size / 2.9)
    second_line_font = ImageFont.truetype('ttf/GoogleSans-Bold.ttf', second_line_font_size)
    second_line_fill_color = (87, 88, 91)

    try:
        name_bbox = name_font.getbbox(name)
        name_text_height = name_bbox[3] - name_bbox[1]
    except AttributeError:
        _, name_text_height = name_font.getsize(name)

    x_position_second_line = 480
    y_position_second_line = 605 + name_text_height + 30

    offsets = [(-1, 0), (0, -1), (1, 0), (0, 1)]

    for dx, dy in offsets:
        draw.text(
            (x_position_second_line + dx, y_position_second_line + dy),
            second_line_text,
            font=second_line_font,
            fill=second_line_fill_color
        )

    draw.text(
        (x_position_second_line, y_position_second_line),
        second_line_text,
        font=second_line_font,
        fill=second_line_fill_color
    )

    credential_text = f'Credential ID: {credential_id}'
    credential_font_size = 30
    credential_font = ImageFont.truetype('ttf/GoogleSans-Italic.ttf', credential_font_size)
    credential_fill_color = (87, 88, 91)

    img_width, img_height = img.size

    x_position_credential = 50
    y_position_credential = img_height - 50

    draw.text(
        (x_position_credential, y_position_credential),
        credential_text,
        font=credential_font,
        fill=credential_fill_color
    )

    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    return img_byte_arr

@app.route('/submit', methods=['POST'])
def submit_data():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    durations = data.get('durations')
    projects = data.get('projects')
    core_or_not = data.get('core_or_not')

    salt = generate_salt()
    string_to_hash = f"{name}-{email}-{durations}-{projects}-{core_or_not}-{salt}"
    hash_object = hashlib.sha256(string_to_hash.encode())
    hash_value = hash_object.hexdigest()

    data_to_store = {
        'name': name,
        'email': email,
        'durations': durations,
        'projects': projects,
        'core_or_not': core_or_not,
        'salt': salt,
        'hash': hash_value
    }

    db.collection('credentials').document(hash_value).set(data_to_store)

    img_byte_arr = add_name_to_image(name, hash_value, projects[0])
    pdf_byte_arr = convert_jpg_to_pdf(img_byte_arr)

    pdf_path = f'temp/{hash_value}.pdf'
    with open(pdf_path, 'wb') as f:
        f.write(pdf_byte_arr.getvalue())

    return jsonify({'hash_id': hash_value, 'pdf_url': f'/download/{hash_value}'}), 200

@app.route('/download/<hash_id>', methods=['GET'])
def download_pdf(hash_id):
    pdf_path = f'temp/{hash_id}.pdf'
    return send_file(pdf_path, download_name='certificate.pdf', as_attachment=True)

def convert_jpg_to_pdf(img_byte_arr):
    image = Image.open(img_byte_arr)
    pdf_byte_arr = io.BytesIO()
    image.convert('RGB').save(pdf_byte_arr, format='PDF')
    pdf_byte_arr.seek(0)
    return pdf_byte_arr

@app.route('/certs/<string:cred_id>', methods=['GET'])
def get_data(cred_id):
    try:
        doc_ref = db.collection('credentials').document(cred_id)
        doc = doc_ref.get()

        if doc.exists:
            return jsonify(doc.to_dict()), 200
        else:
            print(jsonify({'status': '文件不存在', 'error': 'Document not found'}))
            return jsonify({'status': '文件不存在', 'error': 'Document not found'}), 404
    except Exception as e:
        return jsonify({'status': '操作失敗', 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(threaded=True)
