def generate_insights(row):
    """
    Generates human-readable insights based on financial behavior
    """

    insights = []

    # Savings behavior
    if row["savings_rate"] < 5:
        insights.append("Savings rate is critically low, limiting long-term growth.")
    elif row["savings_rate"] < 10:
        insights.append("Savings rate is below recommended levels.")

    # Expense behavior
    if row["expense_ratio"] > 90:
        insights.append("Expenses are extremely high relative to income.")
    elif row["expense_ratio"] > 80:
        insights.append("High expenses are consuming most of the income.")

    # Intention vs reality
    if row["savings_gap"] > 0:
        insights.append("Planned savings were not fully achieved.")

    # Emergency preparedness
    if str(row["emergency_fund"]).lower() != "yes":
        insights.append("Lack of emergency fund reduces future security.")

    # Positive reinforcement
    if not insights:
        insights.append("Financial behavior appears stable and well-balanced.")

    return insights


def detect_resistance(row):
    """
    Detects the PRIMARY reason blocking financial readiness
    (only one dominant resistance is returned)
    """

    # 1️⃣ Wants to save but fails completely
    if row["intended_savings"] > 0 and row["actual_savings"] <= 0:
        return "Strong intention to save exists, but execution is failing."

    # 2️⃣ High spending pressure
    if row["expense_ratio"] > 85:
        return "High spending pressure is preventing effective savings."

    # 3️⃣ Planning mismatch
    if row["savings_gap"] > 0:
        return "Gap between planned and actual savings indicates weak follow-through."

    # 4️⃣ No safety buffer
    if str(row["emergency_fund"]).lower() == "no":
        return "Absence of emergency fund increases financial risk."

    # 5️⃣ No major resistance
    return "No major resistance detected. Financial behavior is reasonably disciplined."