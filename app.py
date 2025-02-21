from flask import Flask, render_template, request, send_file, flash, redirect
import os
import hashlib
import random
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_key'
app.config['UPLOAD_FOLDER'] = 'books'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
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

def is_duplicate(file_path):
    """Check if file is already in the books folder"""
    new_file_hash = get_file_hash(file_path)
    for book in os.listdir(app.config['UPLOAD_FOLDER']):
        book_path = os.path.join(app.config['UPLOAD_FOLDER'], book)
        if get_file_hash(book_path) == new_file_hash:
            
            return True
    return False

def get_random_book(uploaded_book_name):
    """Get a random book that's different from the uploaded one"""
    books = os.listdir(app.config['UPLOAD_FOLDER'])
    books.remove(uploaded_book_name) if uploaded_book_name in books else None
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
            file.save(file_path)

            if is_duplicate(file_path):
                os.remove(file_path)
                flash('This book already exists in our library!')
                return redirect(request.url)

            # Get a random book in exchange
            exchange_book = get_random_book(filename)
            if exchange_book:
                return send_file(
                    os.path.join(app.config['UPLOAD_FOLDER'], exchange_book),
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
    app.run(debug=True) 