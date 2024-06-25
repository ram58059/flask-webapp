from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
from flask_cors import CORS
from flask_oauthlib.client import OAuth
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)
app.secret_key = os.getenv('SECRET_KEY')

# Load data
data = pd.read_excel('data/data.xls', engine='xlrd')

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

@app.route('/')
def index():
    if 'google_token' in session:
        user_info = google.get('userinfo')
        page = request.args.get('page', 1, type=int)
        per_page = 50  # Number of rows per page
        sort_by = request.args.get('sort_by', None)
        sort_order = request.args.get('sort_order', 'asc')

        data_sorted = data
        if sort_by:
            data_sorted = data.sort_values(by=sort_by, ascending=(sort_order == 'asc'))

        total = len(data_sorted)
        start = (page - 1) * per_page
        end = start + per_page
        data_subset = data_sorted.iloc[start:end].to_dict(orient='records')
        
        return render_template('index.html', data=data_subset, page=page, total=total, per_page=per_page, sort_by=sort_by, sort_order=sort_order)
    return redirect(url_for('login'))

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

if __name__ == '__main__':
    app.run(debug=True)
