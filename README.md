# Flask Application

## Description
This Flask application allows users to upload Excel files, view data in a paginated table, perform sorting and searching, and authenticate using Google OAuth.

## Setup Instructions

### Prerequisites
- Python 3.x installed
- Pip package manager

### Installation Steps

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
2. Install dependencies:
    ```bash
   pip install -r requirements.txt
3. Set up environment variables:
- Create a .env file in the root directory.
- Add the following variables to .env:
    ```bash
   SECRET_KEY=your_secret_key_here
   GOOGLE_CONSUMER_KEY=your_google_consumer_key_here
   GOOGLE_CONSUMER_SECRET=your_google_consumer_secret_here
- For testing, you can download .env file from this [link](https://privatebin.net/?940ca857410e4f6b#GuE9BkJDoX9FbZR8y1AcCJ6M5zHutMXH1VoPoJgHxgsD). Link will be expired in 30 days.
4. Run the application:
    ```bash
    python app.py
5. Open your web browser and navigate to http://localhost:5000 to access the application.
