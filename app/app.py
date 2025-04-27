import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import pymongo
import yfinance as yf
import os

from modules.data_processing import calculate_budget, update_budget
from modules.eda import generate_pie_chart
from modules.upi_integration import process_payment
from modules.stock_prediction import predict_stock_prices

# MongoDB Connection
mongo_uri = os.getenv("MONGO_URI", "mongodb+srv://Jai:Jai07ihub@cluster0.k4pik.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
client = pymongo.MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
try:
    client.server_info()
except pymongo.errors.ServerSelectionTimeoutError as err:
    st.error("Cannot connect to MongoDB. Please check your connection.")
    st.stop()

db = client["financial_ai"]
budget_collection = db["budget"]
transactions_collection = db["transactions"]
stocks_collection = db["stocks"]
users_collection = db["users"]

# ----------------- Authentication Functions -----------------
def signup_user(username, password):
    if users_collection.find_one({"username": username}):
        return False, "Username already exists!"
    users_collection.insert_one({"username": username, "password": password})
    return True, "User registered successfully!"

def login_user(username, password):
    user = users_collection.find_one({"username": username, "password": password})
    if user:
        return True
    return False

def show_login_signup():
    st.title("🔒 Welcome to Financial AI Assistant")
    option = st.radio("Select Option:", ["Login", "Sign Up"])

    username = st.text_input("Username")

    if option == "Login":
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if login_user(username, password):
                st.success("Login successful!")
                st.session_state["authenticated"] = True
                st.session_state["username"] = username
                st.rerun()
            else:
                st.error("Invalid username or password.")

    elif option == "Sign Up":
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        if st.button("Sign Up"):
            if password != confirm_password:
                st.error("Passwords do not match!")
            elif not username or not password:
                st.error("Username and password cannot be empty.")
            else:
                success, msg = signup_user(username, password)
                if success:
                    st.success(msg)
                else:
                    st.error(msg)

# ----------------- Profile and Logout Functions -----------------
def show_profile():
    username = st.session_state["username"]
    st.title(f"👤 {username}'s Profile")

    # Display basic user details (here, we just show the username)
    st.write(f"### Username: {username}")
    
    # Add logout button
    if st.button("Logout"):
        st.session_state["authenticated"] = False
        del st.session_state["username"]
        st.success("You have logged out successfully.")
        st.rerun()  # Reload the page to show the login/signup screen

# ----------------- Load Data Functions -----------------
def load_budget(username):
    budget_data = list(budget_collection.find({"username": username}, {"_id": 0}))
    if budget_data:
        return pd.DataFrame(budget_data)
    return None

def load_transactions(username):
    transactions = list(transactions_collection.find({"username": username}, {"_id": 0}))
    if transactions:
        return transactions
    return []

def load_stock_purchases(username):
    stock_data = list(stocks_collection.find({"username": username}, {"_id": 0}))
    if stock_data:
        return stock_data
    return []

# ----------------- Main App -----------------
def main_app():
    username = st.session_state["username"]

    # Initialize session state for budget and transactions
    if "budget_data" not in st.session_state:
        st.session_state["budget_data"] = load_budget(username)

    if "transactions" not in st.session_state:
        st.session_state["transactions"] = load_transactions(username)

    if "stock_purchases" not in st.session_state:
        st.session_state["stock_purchases"] = load_stock_purchases(username)

    st.set_page_config(page_title="Financial AI Assistant", page_icon="💸", layout="wide")

    menu = st.sidebar.radio("Navigation", ["Home", "Transaction History", "Stock Prediction", "Stock Learning", "Profile"])

    if menu == "Profile":
        show_profile()
    elif menu == "Home":
        st.title("💸 Financial AI Assistant")

        # Step 1: Input Monthly Income
        st.markdown("### Enter Monthly Income")
        income = st.number_input("Monthly Income (₹):", min_value=0, step=1000)

        # Step 2: Automatically Generate Budget
        if income > 0:
            st.markdown("### Generated Budget")
            categories = ["Housing", "Food", "Transportation", "Entertainment", "Utilities", "Savings"]
            percentages = [30, 20, 15, 10, 10, 15]  # Budget percentages

            if st.session_state["budget_data"] is None:
                budget = calculate_budget(income, percentages)
                st.session_state["budget_data"] = pd.DataFrame({"Category": categories, "Remaining Budget (₹)": budget})

            budget_df = st.session_state["budget_data"]
            st.dataframe(budget_df)

            # Expense distribution chart
            st.markdown("### 📊 Expense Distribution")
            fig = generate_pie_chart(budget_df["Remaining Budget (₹)"], budget_df["Category"])
            st.pyplot(fig)

            # Payment Feature
            st.markdown("### 💳 UPI Payment")
            payment_category = st.selectbox("Select category to pay:", categories[:-1])
            payment_amount = st.number_input(f"Enter amount to pay for {payment_category}:", min_value=0, step=50)

            if st.button("Make Payment"):
                payment_status, updated_budget = update_budget(
                    st.session_state["budget_data"], payment_category, payment_amount
                )
                st.session_state["budget_data"] = updated_budget

                if "paid" in payment_status:
                    transaction = {"Category": payment_category, "Amount Paid (₹)": payment_amount, "username": username}
                    st.session_state["transactions"].append(transaction)
                    transactions_collection.insert_one(transaction)
                st.success(payment_status)

            # Save budget data
            if st.button("Save Budget Data"):
                budget_collection.delete_many({"username": username})
                budget_collection.insert_many(budget_df.to_dict("records"))
                st.success("Budget data saved successfully!")

        else:
            st.warning("Please enter your monthly income to generate the budget.")

    elif menu == "Transaction History":
        st.title("📜 Transaction History")

        if st.session_state["transactions"]:
            st.markdown("### Payments Made")
            transactions_df = pd.DataFrame(st.session_state["transactions"])
            st.dataframe(transactions_df)

            st.markdown("### Updated Budget")
            st.dataframe(st.session_state["budget_data"])
        else:
            st.info("No transactions made yet.")

    elif menu == "Stock Prediction":
        st.title("📈 Stock Prediction and Investment")

        st.markdown("### Enter Stock Details")
        stock_ticker = st.text_input("Stock Ticker (e.g., AAPL, TSLA):")

        if st.button("Predict Stock Prices"):
            if stock_ticker:
                predicted_prices = predict_stock_prices(stock_ticker)
                st.line_chart(predicted_prices)
            else:
                st.warning("Please enter a valid stock ticker.")

        st.markdown("### Buy Stocks")
        stock_name = st.text_input("Stock Name:")
        stock_price = st.number_input("Stock Price (₹):", min_value=0.0, step=0.01)
        stock_quantity = st.number_input("Quantity:", min_value=1, step=1)

        if st.button("Buy Stock"):
            if stock_name and stock_price > 0 and stock_quantity > 0:
                total_cost = stock_price * stock_quantity
                stock_purchase = {
                    "Stock Name": stock_name,
                    "Stock Price": stock_price,
                    "Quantity": stock_quantity,
                    "Total Cost": total_cost,
                    "username": username  # Save stock purchase to the user's profile
                }
                stocks_collection.insert_one(stock_purchase)
                st.session_state["stock_purchases"].append(stock_purchase)
                st.success(f"Successfully purchased {stock_quantity} of {stock_name} for ₹{total_cost}.")
            else:
                st.warning("Please fill in all fields correctly.")

        st.markdown("### Purchase History")
        if st.session_state["stock_purchases"]:
            purchases_df = pd.DataFrame(st.session_state["stock_purchases"])
            st.dataframe(purchases_df)
        else:
            st.info("No stocks purchased yet.")

    elif menu == "Stock Learning":
        st.title("📘 Stock Learning Center")
        # Content for stock learning section

# ----------------- Run App -----------------
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    show_login_signup()
else:
    main_app()
