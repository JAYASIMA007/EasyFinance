from turtle import st
from flask import Flask, request, jsonify
import hmac
import hashlib

from modules.data_processing import update_budget


app = Flask(__name__)

# Razorpay Webhook Secret
WEBHOOK_SECRET = "your_webhook_secret"

@app.route("/webhook", methods=["POST"])
def razorpay_webhook():
    """
    Webhook to handle Razorpay payment status updates.
    """
    try:
        # Verify Razorpay signature
        payload = request.get_data()
        signature = request.headers.get("X-Razorpay-Signature")

        generated_signature = hmac.new(
            bytes(WEBHOOK_SECRET, 'utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()

        if generated_signature != signature:
            return jsonify({"error": "Invalid signature"}), 403

        # Extract payment status
        webhook_data = request.json
        if webhook_data["event"] == "payment.captured":
            payment_id = webhook_data["payload"]["payment"]["entity"]["id"]
            amount = webhook_data["payload"]["payment"]["entity"]["amount"] / 100  # Convert back to INR
            category = webhook_data["payload"]["payment"]["entity"]["notes"]["category"]

            # Update budget dynamically
            # (Implement the `update_budget()` logic from your app)
            update_budget(st.session_state["budget_data"], category, amount)

            return jsonify({"message": "Budget updated successfully!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400
