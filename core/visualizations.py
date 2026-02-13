import matplotlib
matplotlib.use("Agg")   # ✅ IMPORTANT: non-GUI backend

import pandas as pd
import matplotlib.pyplot as plt
import os


def save_web_plots(df):
    """
    Generates plots for the web app and saves them as images
    with behavioral annotations
    """

    output_dir = "../web/static/plots"
    os.makedirs(output_dir, exist_ok=True)

    # ===============================
    # 1️⃣ Savings vs Expenses (Annotated)
    # ===============================
    savings = df.iloc[0]["actual_savings"]
    expenses = df.iloc[0]["total_expenses"]
    income = df.iloc[0]["income"]

    plt.figure(figsize=(5, 4))
    plt.bar(["Savings", "Expenses"], [savings, expenses])
    plt.title("Savings vs Expenses")
    plt.ylabel("Amount")

    # 🔍 Behavioral annotations
    annotations = []

    savings_rate = (savings / income) * 100 if income > 0 else 0
    expense_ratio = (expenses / income) * 100 if income > 0 else 0

    if savings_rate < 10:
        annotations.append("Low savings rate")
    if expense_ratio > 80:
        annotations.append("High expense pressure")
    if str(df.iloc[0]["emergency_fund"]).lower() == "no":
        annotations.append("No emergency fund")

    if annotations:
        plt.text(
            0.5,
            max(savings, expenses) * 0.9,
            " | ".join(annotations),
            ha="center",
            fontsize=9,
            color="darkred"
        )

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "savings_vs_expenses.png"))
    plt.close()

    # ===============================
    # 2️⃣ Expense Split (Annotated)
    # ===============================
    fixed = df.iloc[0]["fixed_expenses"]
    variable = df.iloc[0]["variable_expenses"]

    plt.figure(figsize=(5, 4))
    plt.pie(
        [fixed, variable],
        labels=["Fixed Expenses", "Variable Expenses"],
        autopct="%1.1f%%"
    )
    plt.title("Expense Composition")

    # 🔍 Annotation for imbalance
    if variable > fixed:
        plt.text(
            0, -1.3,
            "Variable expenses dominate spending",
            ha="center",
            fontsize=9,
            color="darkred"
        )

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "expense_split.png"))
    plt.close()


def save_dashboard_trend(records):
    """
    Saves a mini trend graph for the dashboard with annotations
    """

    import matplotlib
    matplotlib.use("Agg")   # IMPORTANT for Flask
    import matplotlib.pyplot as plt

    months = [r[0] for r in records][:6][::-1]
    scores = [r[1] for r in records][:6][::-1]

    if len(scores) < 2:
        return

    plt.figure(figsize=(4, 2))
    plt.plot(months, scores, marker="o")
    plt.title("Readiness Trend")
    plt.xticks(rotation=45)

    # 🔍 Annotate last change
    delta = scores[-1] - scores[-2]

    if delta > 0:
        note = "Improved due to better control"
        color = "green"
    elif delta < 0:
        note = "Decline due to spending pressure"
        color = "red"
    else:
        note = "Stable behavior"
        color = "gray"

    plt.annotate(
        note,
        (months[-1], scores[-1]),
        textcoords="offset points",
        xytext=(0, 8),
        ha="center",
        fontsize=8,
        color=color
    )

    plt.tight_layout()
    path = os.path.join("static", "plots", "dashboard_trend.png")
    plt.savefig(path)
    plt.close()