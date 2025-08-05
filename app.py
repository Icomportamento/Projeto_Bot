from flask import Flask, request, jsonify
import slack_handler
from config import SLACK_SIGNING_SECRET
from slack_sdk.signature import SignatureVerifier

app = Flask(__name__)
signature_verifier = SignatureVerifier(SLACK_SIGNING_SECRET)

@app.route("/slack/events", methods=["POST"])
def slack_events():
    if not signature_verifier.is_valid_request(request.get_data(), request.headers):
        return "Invalid request signature", 403

    event_data = request.get_json()
    if "challenge" in event_data:
        return jsonify({"challenge": event_data["challenge"]})

    if "event" in event_data:
        slack_handler.handle_event(event_data["event"])

    return "", 200

@app.route("/slack/commands", methods=["POST"])
def slack_commands():
    if not signature_verifier.is_valid_request(request.get_data(), request.headers):
        return "Invalid request signature", 403

    command_payload = request.form.to_dict()
    slack_handler.handle_slash_command(command_payload)
    return "", 200

if __name__ == "__main__":
    app.run(port=3000, debug=True)
