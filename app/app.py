import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from modules.data_processing import calculate_budget, update_budget
from modules.eda import generate_pie_chart
from modules.upi_integration import process_payment
from modules.stock_prediction import predict_stock_prices  # Module for stock prediction
import pymongo

# Initialize MongoDB client with environment variable for cloud compatibility
mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = pymongo.MongoClient(mongo_uri)
db = client["financial_ai"]  # Database name
budget_collection = db["budget"]
transactions_collection = db["transactions"]
stocks_collection = db["stocks"]

# Load budget from MongoDB
def load_budget():
    budget_data = list(budget_collection.find({}, {"_id": 0}))
    return pd.DataFrame(budget_data) if budget_data else None

# Load transactions from MongoDB
def load_transactions():
    transactions = list(transactions_collection.find({}, {"_id": 0}))
    return transactions if transactions else []

# Load stock purchases from MongoDB
def load_stock_purchases():
    stock_data = list(stocks_collection.find({}, {"_id": 0}))
    return stock_data if stock_data else []

# Initialize session state
if "budget_data" not in st.session_state:
    st.session_state.budget_data = load_budget()

if "transactions" not in st.session_state:
    st.session_state.transactions = load_transactions()

if "stock_purchases" not in st.session_state:
    st.session_state.stock_purchases = load_stock_purchases()

# App configuration
st.set_page_config(page_title="Financial AI Assistant", page_icon="💸", layout="wide")

# Sidebar navigation
menu = st.sidebar.radio("Navigation", ["Home", "Transaction History", "Stock Prediction"])

# Page: Home
if menu == "Home":
    st.title("💸 Financial AI Assistant")

    income = st.number_input("### Enter Monthly Income (₹):", min_value=0, step=1000)

    if income > 0:
        st.markdown("### Generated Budget")
        categories = ["Housing", "Food", "Transportation", "Entertainment", "Utilities", "Savings"]
        percentages = [30, 20, 15, 10, 10, 15]

        if st.session_state.budget_data is None:
            budget = calculate_budget(income, percentages)
            st.session_state.budget_data = pd.DataFrame({"Category": categories, "Remaining Budget (₹)": budget})

        budget_df = st.session_state.budget_data
        st.dataframe(budget_df)

        st.markdown("### 📊 Expense Distribution")
        fig = generate_pie_chart(budget_df["Remaining Budget (₹)"], budget_df["Category"])
        st.pyplot(fig)

        st.markdown("### 💳 UPI Payment")
        payment_category = st.selectbox("Select category to pay:", categories[:-1])
        payment_amount = st.number_input(f"Enter amount to pay for {payment_category}:", min_value=0, step=50)

        if st.button("Make Payment"):
            payment_status, updated_budget = update_budget(
                st.session_state.budget_data, payment_category, payment_amount
            )
            st.session_state.budget_data = updated_budget

            if "paid" in payment_status:
                transaction = {"Category": payment_category, "Amount Paid (₹)": payment_amount}
                st.session_state.transactions.append(transaction)
                transactions_collection.insert_one(transaction)
            st.success(payment_status)

        if st.button("Save Budget Data"):
            budget_collection.delete_many({})
            budget_collection.insert_many(budget_df.to_dict("records"))
            st.success("Budget data saved successfully!")
    else:
        st.warning("Please enter your monthly income to generate the budget.")

# Page: Transaction History
elif menu == "Transaction History":
    st.title("📜 Transaction History")

    if st.session_state.transactions:
        st.markdown("### Payments Made")
        transactions_df = pd.DataFrame(st.session_state.transactions)
        st.dataframe(transactions_df)

        st.markdown("### Updated Budget")
        st.dataframe(st.session_state.budget_data)
    else:
        st.info("No transactions made yet.")

# Page: Stock Prediction
elif menu == "Stock Prediction":
    st.title("📈 Stock Prediction and Investment")

    stock_ticker = st.text_input("### Enter Stock Ticker (e.g., AAPL, TSLA):")

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
                "Total Cost": total_cost
            }

            stocks_collection.insert_one(stock_purchase)
            st.session_state.stock_purchases.append(stock_purchase)
            st.success(f"Successfully purchased {stock_quantity} of {stock_name} for ₹{total_cost}.")
        else:
            st.warning("Please fill in all fields correctly.")

    st.markdown("### Purchase History")
    if st.session_state.stock_purchases:
        purchases_df = pd.DataFrame(st.session_state.stock_purchases)
        st.dataframe(purchases_df)
    else:
        st.info("No stocks purchased yet.")

# Run on assigned port (Render)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8501))
    import streamlit.web.bootstrap
    streamlit.web.bootstrap.run("app.py", "", [], flag_options={"server.port": port})