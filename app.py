from flask import Flask, render_template, request, redirect, url_for, session, flash
import pandas as pd
from flask_cors import CORS
from flask_oauthlib.client import OAuth
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
UPLOAD_FOLDER = 'data'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'xls'}

# OAuth setup
oauth = OAuth(app)
google = oauth.remote_app(
    'google',
    consumer_key=os.getenv('GOOGLE_CONSUMER_KEY'),
    consumer_secret=os.getenv('GOOGLE_CONSUMER_SECRET'),
    request_token_params={
        'scope': 'email',
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)

# Sample data initialization
data = pd.DataFrame()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    if 'google_token' in session:
        if data.empty:
            return render_template('index.html', data=None)
        
        page = request.args.get('page', 1, type=int)
        per_page = 50  # Number of rows per page
        sort_by = request.args.get('sort_by', None)
        sort_order = request.args.get('sort_order', 'asc')
        search_column = request.args.get('search_column', None)
        search_query = request.args.get('search_query', '')

        if search_query:
            data_filtered = data[data[search_column].astype(str).str.contains(search_query, case=False, na=False)]
        else:
            data_filtered = data

        if sort_by:
            data_filtered = data_filtered.sort_values(by=sort_by, ascending=(sort_order == 'asc'))
        
        total = len(data_filtered) - 1
        start = (page - 1) * per_page
        end = start + per_page
        
        if end > total:
            end = total
        
        data_subset = data_filtered.iloc[start:end].to_dict(orient='records')
        current_rows_per_page = end - start
        
        return render_template('index.html', current_rows_per_page=current_rows_per_page, data=data_subset, page=page, total=total, per_page=per_page, sort_by=sort_by, sort_order=sort_order, search_column=search_column, search_query=search_query)
    return redirect(url_for('google_signin'))


@app.route('/google-signin')
def google_signin():
    return render_template('signin.html')

@app.route('/login')
def login():
    return google.authorize(callback=url_for('authorized', _external=True))

@app.route('/logout')
def logout():
    session.pop('google_token')
    return redirect(url_for('index'))

@app.route('/login/authorized')
def authorized():
    response = google.authorized_response()
    if response is None or response.get('access_token') is None:
        return 'Access denied: reason={} error={}'.format(
            request.args['error_reason'],
            request.args['error_description']
        )
    session['google_token'] = (response['access_token'], '')
    return redirect(url_for('index'))

@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'google_token' not in session:
        return redirect(url_for('login'))
    
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        filename = 'data.xls'  # Save as a fixed name
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        global data
        data = pd.read_excel(file_path, engine='xlrd')
        
        # Clear search parameters on file upload
        session.pop('search_column', None)
        session.pop('search_query', None)
        
        return redirect(url_for('index'))
    
    flash('Invalid file format')
    return redirect(request.url)

@app.route('/clear-data')
def clear_data():
    global data
    data = pd.DataFrame()  # Clear data
    return redirect(url_for('index'))

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
