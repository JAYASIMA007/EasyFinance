import matplotlib.pyplot as plt

def generate_pie_chart(data, labels):
    """
    Generate a pie chart for budget distribution.

    Args:
        data (list): Budget values for each category.
        labels (list): Category labels.

    Returns:
        matplotlib.figure.Figure: The pie chart figure.
    """
    fig, ax = plt.subplots()
    ax.pie(data, labels=labels, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
    ax.axis('equal')  # Ensure the pie chart is a circle
    return fig
