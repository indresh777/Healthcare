# data.py

from firebase_admin import auth, firestore
from datetime import datetime

db = firestore.client()

def firebase_register_user(password, username):
    try:
        # Firebase Authentication always needs an email to create a user, so we simulate one
        fake_email = f"{username}@example.com"  # Fake email for firebase

        user = auth.create_user(email=fake_email, password=password)
        user_id = user.uid

        # Save username separately in Firestore
        db.collection("users").document(user_id).set({
            "username": username,
            "createdAt": datetime.utcnow()
        })

        return {"success": True, "user_id": user_id, "message": f"User {username} registered successfully!"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def firebase_login_user(username, password):
    try:
        users_ref = db.collection("users")
        query = users_ref.where("username", "==", username).stream()
        user_doc = None
        for doc in query:
            user_doc = doc
            break

        if user_doc:
            # You can also validate password if you manage passwords manually (advanced)
            return {"success": True, "user_id": user_doc.id, "username": username}
        else:
            return {"success": False, "error": "User not found."}
    except Exception as e:
        return {"success": False, "error": str(e)}

def firebase_add_appointment(user_id, appointment_details):
    try:
        appointment_ref = db.collection("appointments").document(user_id).collection("userAppointments").document()
        appointment_ref.set(appointment_details)
        return {"success": True, "message": "Appointment saved to Firebase."}
    except Exception as e:
        return {"success": False, "error": str(e)}
