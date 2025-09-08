from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import json

app = Flask(__name__)

# Load dataset
with open("health_chatbot_dataset.json", "r", encoding="utf-8") as f:
    health_data = json.load(f)

def get_response(text):
    t = text.lower()
    replies = []

    # Check all diseases
    for disease, details in health_data.get("diseases", {}).items():
        if disease in t and "symptom" in t:
            replies.append(f"{disease.capitalize()} symptoms: {', '.join(details['symptoms'])}")

    # Check vaccination schedule
    for vaccine, schedule in health_data.get("vaccination_schedule", {}).items():
        if vaccine in t and ("vaccine" in t or "vaccination" in t):
            replies.append(f"{vaccine.capitalize()} vaccination schedule: {schedule}")

    # Return all replies if any, else default message
    if replies:
        return "\n".join(replies)
    
    return (
        "Sorry, I didn't understand. You can ask about diseases (e.g., dengue, malaria) "
        "or vaccines (e.g., polio, hepatitis)."
    )

@app.route("/bot", methods=["POST"])
def bot():
    incoming_msg = request.form.get("Body", "")
    print(f"Incoming message: {incoming_msg}")  # Logging
    reply_text = get_response(incoming_msg)
    resp = MessagingResponse()
    resp.message(reply_text)
    return str(resp)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
