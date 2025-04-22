from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
import os
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'pdf', 'txt', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_pdf_filename(original_filename):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = secure_filename(original_filename)
    return f"pdf_{timestamp}_{safe_name}"


def generate_file_filename(original_filename):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = secure_filename(original_filename)
    return f"file_{timestamp}_{safe_name}"


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload-pdf', methods=['GET', 'POST'])
def upload_pdf():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename) and file.filename.rsplit('.', 1)[1].lower() == 'pdf':
            filename = generate_pdf_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash('PDF successfully uploaded')
            return redirect(url_for('upload_pdf'))
        else:
            flash('Allowed file type is PDF only')

    return render_template('upload_pdf.html')


@app.route('/view-file', methods=['GET', 'POST'])
def view_file():
    # Get list of existing files
    existing_files = []
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.isfile(path):
            existing_files.append(filename)

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'upload':
            # Handle file upload and view
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)

            file = request.files['file']
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)

            if file and allowed_file(file.filename):
                filename = generate_file_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)

                file_ext = filename.rsplit('.', 1)[1].lower()
                if file_ext in ['png', 'jpg', 'jpeg', 'gif']:
                    return render_template('view_file.html', file_type='image', filename=filename,
                                           existing_files=existing_files)
                elif file_ext == 'pdf':
                    return render_template('view_file.html', file_type='pdf', filename=filename,
                                           existing_files=existing_files)
                elif file_ext in ['txt']:
                    with open(filepath, 'r') as f:
                        content = f.read()
                    return render_template('view_file.html', file_type='text', content=content, filename=filename,
                                           existing_files=existing_files)
                else:
                    return render_template('view_file.html', file_type='download', filename=filename,
                                           existing_files=existing_files)
            else:
                flash('Allowed file types are: pdf, txt, png, jpg, jpeg, gif, doc, docx')

        elif action == 'view':
            # Handle view only
            filename = request.form.get('existing-file')
            if not filename:
                flash('No file selected')
                return redirect(request.url)

            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if not os.path.exists(filepath):
                flash('File not found')
                return redirect(request.url)

            file_ext = filename.rsplit('.', 1)[1].lower()
            if file_ext in ['png', 'jpg', 'jpeg', 'gif']:
                return render_template('view_file.html', file_type='image', filename=filename,
                                       existing_files=existing_files)
            elif file_ext == 'pdf':
                return render_template('view_file.html', file_type='pdf', filename=filename,
                                       existing_files=existing_files)
            elif file_ext in ['txt']:
                with open(filepath, 'r') as f:
                    content = f.read()
                return render_template('view_file.html', file_type='text', content=content, filename=filename,
                                       existing_files=existing_files)
            else:
                return render_template('view_file.html', file_type='download', filename=filename,
                                       existing_files=existing_files)

    return render_template('view_file.html', existing_files=existing_files)


@app.route('/browse-files')
def browse_files():
    files = []
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.isfile(path):
            files.append(filename)
    return render_template('browse_files.html', files=files)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    app.run(debug=True)