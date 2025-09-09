from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import json
from difflib import get_close_matches

app = Flask(__name__)

# Load dataset
with open("health_chatbot_dataset.json", "r", encoding="utf-8") as f:
    health_data = json.load(f)

# Track first interaction per user
first_interaction = {}

def get_greeting():
    greetings = health_data.get("greetings", {})
    return list(greetings.values())[0]

def get_response(text, user_id):
    t = text.lower()
    replies = []

    # First interaction greeting
    if not first_interaction.get(user_id, False):
        first_interaction[user_id] = True
        return get_greeting()

    # Diseases info
    for disease, details in health_data.get("diseases", {}).items():
        if disease in t and ("symptom" in t or "sign" in t):
            replies.append(
                f"{disease.capitalize()} info:\nSymptoms: {', '.join(details['symptoms'])}\n"
                f"Treatment: {', '.join(details['treatment'])}\nPrevention: {', '.join(details['prevention'])}"
            )

    # Symptom checker
    for combo, possible_diseases in health_data.get("symptom_checker", {}).items():
        if all(symptom.strip() in t for symptom in combo.split("+")):
            replies.append(f"Based on your symptoms, possible diseases: {', '.join(possible_diseases)}")

    # Fuzzy disease suggestion
    if not replies:
        possible = get_close_matches(t, health_data.get("diseases", {}).keys(), n=1, cutoff=0.6)
        if possible:
            replies.append(f"Did you mean '{possible[0]}'?")

    # Vaccination info
    for vaccine, schedule in health_data.get("vaccination_schedule", {}).items():
        if vaccine in t and ("vaccine" in t or "vaccination" in t):
            replies.append(f"{vaccine.capitalize()} vaccination schedule: {schedule}")

    # First aid
    for aid, steps in health_data.get("first_aid", {}).items():
        if aid in t:
            replies.append(f"First Aid for {aid}: {steps}")

    # Emergency numbers
    for number, contact in health_data.get("emergency_numbers", {}).items():
        if number in t:
            replies.append(f"{number.capitalize()} emergency contact: {contact}")

    # FAQ
    for key, answer in health_data.get("faq", {}).items():
        if key.replace("_", " ") in t:
            replies.append(answer)

    # Default fallback
    if not replies:
        return (
            "Sorry, I didn't understand. You can ask about diseases, vaccination, first aid, "
            "emergency contacts, or health programs."
        )

    return "\n\n".join(replies)

@app.route("/bot", methods=["POST"])
def bot():
    incoming_msg = request.form.get("Body", "")
    user_id = request.form.get("From", "anonymous")
    print(f"Incoming message from {user_id}: {incoming_msg}")
    reply_text = get_response(incoming_msg, user_id)
    resp = MessagingResponse()
    resp.message(reply_text)
    return str(resp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
