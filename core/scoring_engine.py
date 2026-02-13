import pandas as pd
from insight_generator import generate_insights, detect_resistance


def load_data(file_path):
    data = pd.read_csv(file_path)
    return data


def calculate_metrics(df):
    df["savings_rate"] = (df["actual_savings"] / df["income"]) * 100
    df["total_expenses"] = df["fixed_expenses"] + df["variable_expenses"]
    df["expense_ratio"] = (df["total_expenses"] / df["income"]) * 100
    df["savings_gap"] = df["intended_savings"] - df["actual_savings"]
    return df


def calculate_readiness_score(row):
    score = 0

    # Savings Rate (40)
    if row["savings_rate"] >= 20:
        score += 40
    elif row["savings_rate"] >= 10:
        score += 25
    elif row["savings_rate"] > 0:
        score += 10

    # Expense Control (25)
    if row["expense_ratio"] <= 60:
        score += 25
    elif row["expense_ratio"] <= 80:
        score += 15
    elif row["expense_ratio"] <= 95:
        score += 5

    # Planning Discipline (20)
    if row["savings_gap"] <= 0:
        score += 20
    elif row["savings_gap"] <= row["intended_savings"] * 0.5:
        score += 10

    # Emergency Readiness (15)
    if str(row["emergency_fund"]).lower() == "yes":
        score += 15

    return score


def calculate_score_breakdown(row):
    breakdown = {}

    # Savings Rate
    if row["savings_rate"] >= 20:
        breakdown["Savings Rate"] = 40
    elif row["savings_rate"] >= 10:
        breakdown["Savings Rate"] = 25
    elif row["savings_rate"] > 0:
        breakdown["Savings Rate"] = 10
    else:
        breakdown["Savings Rate"] = 0

    # Expense Control
    if row["expense_ratio"] <= 60:
        breakdown["Expense Control"] = 25
    elif row["expense_ratio"] <= 80:
        breakdown["Expense Control"] = 15
    elif row["expense_ratio"] <= 95:
        breakdown["Expense Control"] = 5
    else:
        breakdown["Expense Control"] = 0

    # Planning Discipline
    if row["savings_gap"] <= 0:
        breakdown["Planning Discipline"] = 20
    elif row["savings_gap"] <= row["intended_savings"] * 0.5:
        breakdown["Planning Discipline"] = 10
    else:
        breakdown["Planning Discipline"] = 0

    # Emergency Readiness
    if str(row["emergency_fund"]).lower() == "yes":
        breakdown["Emergency Readiness"] = 15
    else:
        breakdown["Emergency Readiness"] = 0

    return breakdown


def classify_readiness(score):
    if score >= 70:
        return "Strong"
    elif score >= 40:
        return "Medium"
    else:
        return "Low"


def generate_user_report(result):
    lines = []
    lines.append("FUTURE READINESS REPORT")
    lines.append("=" * 30)
    lines.append(f"Readiness Score : {result['readiness_score']}")
    lines.append(f"Readiness Level : {result['readiness_level']}")
    lines.append("")
    lines.append(f"Resistance Reason: {result['resistance_reason']}")
    lines.append("")
    lines.append("Score Breakdown:")
    for key, value in result["score_breakdown"].items():
        lines.append(f"- {key}: {value}")
    lines.append("")
    lines.append("Insights:")
    for insight in result["insights"]:
        lines.append(f"- {insight}")

    return "\n".join(lines)
def simulate_expense_reduction(row, reduction_percent=10):
    """
    Simulates readiness score if variable expenses are reduced
    by a given percentage (default: 10%)
    """

    simulated = row.copy()

    reduction_amount = simulated["variable_expenses"] * (reduction_percent / 100)

    simulated["variable_expenses"] = max(
        0, simulated["variable_expenses"] - reduction_amount
    )

    simulated["actual_savings"] = (
        simulated["income"]
        - simulated["fixed_expenses"]
        - simulated["variable_expenses"]
    )

    simulated["savings_rate"] = (
        simulated["actual_savings"] / simulated["income"]
    ) * 100

    simulated["total_expenses"] = (
        simulated["fixed_expenses"] + simulated["variable_expenses"]
    )

    simulated["expense_ratio"] = (
        simulated["total_expenses"] / simulated["income"]
    ) * 100

    simulated["savings_gap"] = (
        simulated["intended_savings"] - simulated["actual_savings"]
    )

    new_score = calculate_readiness_score(simulated)
    new_level = classify_readiness(new_score)

    return new_score, new_level, round(reduction_amount, 2)

def simulate_multiple_reductions(row):
    """
    Simulates readiness score under different expense reduction levels
    """
    results = []

    for percent in [10, 20]:
        score, level, reduction_amount = simulate_expense_reduction(
            row, reduction_percent=percent
        )
        results.append({
            "percent": percent,
            "reduction_amount": reduction_amount,
            "score": score,
            "level": level
        })

    return results



def generate_text_report(df, output_path):
    with open(output_path, "w") as file:
        file.write("FUTURE READINESS REPORT\n")
        file.write("=" * 30 + "\n")

        for _, row in df.iterrows():
            file.write(f"\nMonth: {row['month']}\n")
            file.write(f"Readiness Score: {row['readiness_score']} ({row['readiness_level']})\n")
            file.write(f"Resistance Reason: {row['resistance_reason']}\n")
            file.write("Insights:\n")
            for insight in row["insights"]:
                file.write(f"- {insight}\n")
def determine_financial_profile(row):
    """
    Determines financial personality based on behavior patterns
    """

    if row["savings_rate"] >= 20 and str(row["emergency_fund"]).lower() == "yes":
        return "Financially Balanced and Secure"

    if row["savings_rate"] >= 20 and str(row["emergency_fund"]).lower() == "no":
        return "Strong Saver but Emergency-Vulnerable"

    if row["expense_ratio"] > 80 and row["savings_rate"] > 0:
        return "Income Stable but Expense-Pressured"

    if row["savings_rate"] <= 0:
        return "Income Consumed with No Savings Buffer"

    if row["savings_gap"] > 0:
        return "Planned Saver with Execution Gaps"

    return "Moderately Stable Financial Behavior"
def generate_risk_flags(row):
    """
    Generates risk indicators based on financial behavior
    """

    flags = []

    if str(row["emergency_fund"]).lower() == "no":
        flags.append(("High", "No emergency fund available"))

    if row["expense_ratio"] > 80:
        flags.append(("Medium", "Expenses exceed 80% of income"))

    if row["savings_rate"] > 0:
        flags.append(("Low", "Positive savings behavior detected"))

    if row["savings_gap"] > 0:
        flags.append(("Medium", "Planned savings not fully achieved"))

    return flags



# Run only when executed directly (not when imported)
if __name__ == "__main__":
    file_path = "../data/monthly_finance.csv"

    df = load_data(file_path)
    df = calculate_metrics(df)

    df["readiness_score"] = df.apply(calculate_readiness_score, axis=1)
    df["readiness_level"] = df["readiness_score"].apply(classify_readiness)
    df["score_breakdown"] = df.apply(calculate_score_breakdown, axis=1)
    df["insights"] = df.apply(generate_insights, axis=1)
    df["resistance_reason"] = df.apply(detect_resistance, axis=1)

    print("Future Readiness Analysis:")
    for _, row in df.iterrows():
        print("\nMonth:", row["month"])
        print("Readiness Score:", row["readiness_score"])
        print("Readiness Level:", row["readiness_level"])
        print("Resistance Reason:", row["resistance_reason"])
        print("Insights:")
        for insight in row["insights"]:
            print("-", insight)

    report_path = "../reports/future_readiness_report.txt"
    generate_text_report(df, report_path)
