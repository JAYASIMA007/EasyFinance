import razorpay
import time

# Razorpay API credentials (replace with your actual keys)
RAZORPAY_KEY_ID = "your_key_id"
RAZORPAY_KEY_SECRET = "your_key_secret"

# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

def create_upi_payment(amount, payment_category):
    """
    Create a Razorpay payment order for UPI.
    
    Args:
        amount (int): Payment amount in INR.
        payment_category (str): Category for which the payment is made.
        
    Returns:
        dict: Payment details with UPI link.
    """
    try:
        # Convert amount to paise (Razorpay uses paise)
        amount_paise = amount * 100

        # Create order
        order = razorpay_client.order.create({
            "amount": amount_paise,
            "currency": "INR",
            "payment_capture": 1
        })

        # Generate UPI payment link
        payment_link = razorpay_client.payment_link.create({
            "amount": amount_paise,
            "currency": "INR",
            "accept_partial": False,
            "reference_id": f"UPI-{int(time.time())}",
            "description": f"Payment for {payment_category}",
            "upi": {"vpa": "user@upi"},
            "notify": {"sms": True, "email": True}
        })

        return {
            "payment_status": "Payment link generated successfully.",
            "payment_link": payment_link["short_url"]
        }

    except Exception as e:
        return {"payment_status": f"Error: {str(e)}"}
