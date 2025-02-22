from flask import Flask, render_template, request, send_file, flash, redirect
import os
import hashlib
import random
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['UPLOAD_FOLDER'] = 'books'
app.config['SEND_FOLDER'] = 'send_Books'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16MB max
ALLOWED_EXTENSIONS = {'pdf', 'epub', 'mobi'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_hash(file_path):
    """Calculate SHA-256 hash of a file"""
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

def is_duplicate(filename):
    """Check if file is already in the books folder based on filename"""
    return filename in os.listdir(app.config['UPLOAD_FOLDER'])

def get_random_book(uploaded_book_name):
    """Get a random book that's different from the uploaded one"""
    books = os.listdir(app.config['SEND_FOLDER'])
    if uploaded_book_name in books:
        books.remove(uploaded_book_name)
    return random.choice(books) if books else None

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'book' not in request.files:
            flash('No file uploaded')
            return redirect(request.url)
        
        file = request.files['book']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            # Check for duplicates based on filename before saving
            if is_duplicate(filename):
                flash('This book already exists in our library! File not saved.')
                return redirect(request.url)

            # Save the file if it's not a duplicate
            file.save(file_path)

            # Get a random book from the send_Books folder
            exchange_book = get_random_book(filename)
            if exchange_book:
                return send_file(
                    os.path.join(app.config['SEND_FOLDER'], exchange_book),
                    as_attachment=True,
                    download_name=exchange_book
                )
            else:
                flash('Successfully uploaded! No books available for exchange at the moment.')
                return redirect(request.url)

        flash('Invalid file type. Allowed types are: pdf, epub, mobi')
        return redirect(request.url)

    return render_template('index.html')

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['SEND_FOLDER'], exist_ok=True)
    app.run(debug=True) 