from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS, cross_origin
import os
import pandas as pd
import glob

app = Flask(__name__, static_folder='../frontend/build', static_url_path='/')
CORS(app)

UPLOAD_FOLDER = './uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
rows_per_page = 10

@app.route('/')
def serve():
    return app.send_static_file('index.html')

@app.route('/upload', methods=['POST'])
@cross_origin()
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        files_path = app.config['UPLOAD_FOLDER']
        if os.path.exists(files_path):
            files = glob.glob(os.path.join(files_path, '*'))
            for f in files:
                os.remove(f)
        filename = file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        return jsonify({'message': 'File uploaded successfully', 'filename': filename}), 200

@app.route('/data', methods=['GET'])
@cross_origin()
def get_data():
    filename = request.args.get('filename')
    page = int(request.args.get('page', 0))
    sort_column = request.args.get('sortColumn', '')
    sort_direction = request.args.get('sortDirection', 'asc')
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    
    try:
        df = pd.read_excel(file_path)
        
        # Replace NaN values only in specific columns
        nan_replacements = {col: 'N/A' for col in df.columns if df[col].dtype == 'float64'}
        df.fillna(value=nan_replacements, inplace=True)
        
        if sort_column:
            df.sort_values(by=sort_column, ascending=(sort_direction == 'asc'), inplace=True)
        
        start_row = page * rows_per_page
        end_row = start_row + rows_per_page
        data = df.iloc[start_row:end_row].to_dict(orient='records')
        headers = df.columns.tolist()
        
        return jsonify({'data': data, 'headers': headers, 'total_rows': len(df)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/clear', methods=['POST'])
@cross_origin()
def clear_file():
    filename = request.json.get('filename')
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return jsonify({'message': 'File cleared successfully'}), 200
    else:
        return jsonify({'error': 'File not found'}), 404

@app.route('/filter', methods=['GET'])
@cross_origin()
def filter_data():
    filename = request.args.get('filename')
    column = request.args.get('column')
    query = request.args.get('query')
    page = int(request.args.get('page', 0))

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    try:
        df = pd.read_excel(file_path)
        if column not in df.columns:
            return jsonify({'error': f'Column "{column}" not found'}), 400
        
        filtered_df = df[df[column].astype(str).str.contains(query, case=False, na=False)]
        total_rows = len(filtered_df)
        start_row = page * rows_per_page
        end_row = start_row + rows_per_page
        paginated_data = filtered_df.iloc[start_row:end_row].to_dict(orient='records')
        headers = df.columns.tolist()

        return jsonify({'data': paginated_data, 'headers': headers, 'total_rows': total_rows}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)