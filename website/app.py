from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import json
from datetime import datetime

app = Flask(__name__, static_folder='static', template_folder='templates')


# Load intents.json at startup
def load_intents(path):
    """Load intents from a JSON file."""
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print(f"[ERROR] Failed to decode intents.json: {e}")
    else:
        print("[WARNING] intents.json not found in static folder.")
    return {}

# Initialize intents from static folder
intents_path = os.path.join('intents.json')
intents = load_intents(intents_path)

# In-memory storage for appointments and chat logs (replace with database in the future)

@app.route('/')
def index():
    """Render the home page."""
    return render_template('index.html')

def match_intent(user_input):
    """Match user input to known intents."""
    for intent in intents.get("intents", []):
        for pattern in intent.get("patterns", []):
            if pattern.lower() in user_input:
                return intent.get("responses", ["I'm not sure I understand."])[0]
    return "I'm not sure I understand."

@app.route('/chat', methods=['POST'])
def chat():
    """Handle user chat and return bot response."""
    data = request.get_json()
    user_input = data.get('message', '').strip().lower()

    if not user_input:
        return jsonify({'response': "Please say something!"})

    # Match the user's message to an intent
    response = match_intent(user_input)

    # Log the chat
    chat_logs.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "user": user_input,
        "bot": response
    })

    return jsonify({'response': response})

@app.route('/intents.json')
def get_intents():
    """Serve the intents.json file."""
    return send_from_directory('static/intents.json')

@app.route('/appointment', methods=['GET', 'POST'])
def appointment():
    """Handle appointment bookings."""
    if request.method == 'POST':
        # Get appointment details from form data
        data = request.form.to_dict()
        data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # Append appointment to in-memory list (replace with a database in production)
        appointments.append(data)
        print("[INFO] Appointment saved:", data)

        # Return success page
        return render_template('appointment.html', success=True)

    # Render the appointment form
    return render_template('appointment.html')

@app.route('/backup')
def backup():
    """Display backup of appointments and chat logs."""
    return render_template('backup.html', appointments=appointments, chat_logs=chat_logs)

@app.route('/export_backup')
def export_backup():
    """Export backup data to a JSON file."""
    backup_data = {
        "appointments": appointments,
        "chat_logs": chat_logs
    }

    # Save the backup to a JSON file (future enhancement: store in cloud or database)
    backup_file_path = os.path.join(app.static_folder, 'backup.json')
    with open(backup_file_path, 'w', encoding='utf-8') as f:
        json.dump(backup_data, f, ensure_ascii=False, indent=4)
    
    return jsonify({"message": "Backup exported successfully!", "file_path": backup_file_path})

@app.route('/restore_backup', methods=['POST'])
def restore_backup():
    """Restore backup from a JSON file."""
    data = request.get_json()

    if not data.get("file_path"):
        return jsonify({"error": "No file path provided for restore."}), 400

    # Path to backup file (could be uploaded or selected from the static folder)
    file_path = data.get("file_path")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)

            # Restore appointments and chat logs from the backup
            global appointments, chat_logs
            appointments = backup_data.get("appointments", [])
            chat_logs = backup_data.get("chat_logs", [])
        
        return jsonify({"message": "Backup restored successfully!"})

    except Exception as e:
        return jsonify({"error": f"Failed to restore backup: {str(e)}"}), 500

@app.route('/add_intent', methods=['POST'])
def add_intent():
    """Add a new intent to the intents.json file."""
    data = request.get_json()

    # Example data format for adding a new intent
    new_intent = {
        "tag": data.get("tag"),
        "patterns": data.get("patterns"),
        "responses": data.get("responses")
    }

    # Load current intents and add the new intent
    global intents
    intents["intents"].append(new_intent)

    # Save the updated intents back to the intents.json file
    with open(intents_path, 'w', encoding='utf-8') as f:
        json.dump(intents, f, ensure_ascii=False, indent=4)

    return jsonify({"message": "New intent added successfully!"})

if __name__ == '__main__':
    app.run(debug=True)
