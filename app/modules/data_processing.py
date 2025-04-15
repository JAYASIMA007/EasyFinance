def calculate_budget(income, percentages):
    """
    Distribute income into budget categories based on predefined percentages.

    Args:
        income (int): Total monthly income.
        percentages (list): List of percentage allocations for each category.

    Returns:
        list: Allocated budget amounts for each category.
    """
    return [round(income * (percent / 100)) for percent in percentages]


def update_budget(budget_df, category, amount):
    """
    Deduct payment amount from the selected category in the budget.

    Args:
        budget_df (pd.DataFrame): The current budget data.
        category (str): The category to deduct the amount from.
        amount (int): The amount to deduct.

    Returns:
        tuple: Payment status (str) and updated budget (pd.DataFrame).
    """
    index = budget_df[budget_df["Category"] == category].index[0]
    if budget_df.at[index, "Remaining Budget (₹)"] >= amount:
        budget_df.at[index, "Remaining Budget (₹)"] -= amount
        return f"₹{amount} paid successfully for {category}!", budget_df
    else:
        return f"Insufficient budget in {category}. Please try a smaller amount.", budget_df
