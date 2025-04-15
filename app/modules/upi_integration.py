def process_payment(amount, category):
    """
    Mock function to process UPI payments.

    Args:
        amount (int): Payment amount.
        category (str): Category for payment.

    Returns:
        str: Payment success or failure message.
    """
    if amount > 0:
        return f"₹{amount} paid successfully for {category}!"
    else:
        return "Invalid payment amount. Please try again."
