from flask import Flask, render_template, request, jsonify
import database # Your existing database.py file

# Initialize the Flask application
app = Flask(__name__)

@app.route('/')
def home():
    """
    This is the main route. It serves the user interface (the HTML page).
    """
    # 'render_template' looks for the file in a folder named 'templates'
    return render_template('index.html')

@app.route('/api/search')
def api_search():
    """
    This is the API route. The frontend will send requests here.
    It finds empty rooms and returns them as data.
    """
    # Get parameters from the URL (e.g., ?day=M&start_time=900...)
    day = request.args.get('day')
    start_time_str = request.args.get('start_time')
    end_time_str = request.args.get('end_time')
    building = request.args.get('building')

    # Basic validation
    if not all([day, start_time_str, end_time_str]):
        return jsonify({"error": "Missing required parameters"}), 400
    try:
        start_time = int(start_time_str)
        end_time = int(end_time_str)
    except ValueError:
        return jsonify({"error": "Invalid time format"}), 400

    # Use the same database function you already wrote!
    building_filter = None if building == "All Buildings" else building
    empty_rooms = database.find_empty_rooms(day, start_time, end_time, building_filter)

    # Return the results as JSON data
    return jsonify(empty_rooms)

# This part is optional but good practice for local testing
if __name__ == '__main__':
    app.run(debug=True)