from flask import Flask, render_template, request, session, redirect, Response
import pandas as pd
import sys
import os

# ---------- CORE PATH ----------
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "core"))
)

from scoring_engine import (
    calculate_metrics,
    calculate_readiness_score,
    classify_readiness,
    calculate_score_breakdown,
    generate_user_report,
    simulate_multiple_reductions,
    determine_financial_profile,
    generate_risk_flags
)

from insight_generator import generate_insights, detect_resistance
from visualizations import save_web_plots, save_dashboard_trend
from history_db import get_connection as get_history_connection

app = Flask(__name__)
app.secret_key = "financial_readiness_secret"


# ---------- HOME ----------
@app.route("/")
def home():
    return redirect("/login")


# ---------- LOGIN ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session["user"] = request.form["email"]
        return redirect("/dashboard")
    return render_template("login.html")


# ---------- SIGNUP ----------
@app.route("/signup")
def signup():
    return render_template("signup.html")


# ---------- DASHBOARD ----------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")

    conn = get_history_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT month, readiness_score, financial_profile
        FROM readiness_history
        WHERE user_email = ?
        ORDER BY month DESC
    """, (session["user"],))
    records = cursor.fetchall()
    conn.close()

    assessment_count = len(records)
    last_score = records[0][1] if assessment_count else None
    last_profile = records[0][2] if assessment_count else None
    trend = "stable"

    if assessment_count >= 2:
        if records[0][1] > records[1][1]:
            trend = "up"
        elif records[0][1] < records[1][1]:
            trend = "down"

    trend_message = "No previous data to compare."
    if assessment_count >= 2:
        trend_message = {
            "up": "Your readiness improved compared to last month.",
            "down": "Your readiness declined compared to last month.",
            "stable": "Your financial behavior is stable."
        }[trend]

    next_action = {
        "up": "Maintain saving discipline and avoid lifestyle inflation.",
        "down": "Focus on reducing variable expenses next month.",
        "stable": "Improve savings consistency."
    }.get(trend, "Start tracking expenses.")

    personal_message = "Start your first assessment to understand your financial readiness."
    if assessment_count >= 2:
        personal_message = {
            "up": "Your decisions are improving readiness. Consistency is paying off.",
            "down": "Recent decisions reduced readiness. Review spending carefully.",
            "stable": "Behavior is stable. Small improvements can boost readiness."
        }[trend]

    if assessment_count >= 2:
        save_dashboard_trend(records)

    return render_template(
        "dashboard.html",
        user=session["user"],
        last_score=last_score,
        trend=trend,
        trend_message=trend_message,
        next_action=next_action,
        personal_message=personal_message,
        last_profile=last_profile,
        assessment_count=assessment_count
    )


# ---------- HISTORY ----------
@app.route("/history")
def history():
    if "user" not in session:
        return redirect("/login")

    conn = get_history_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT month, readiness_score, readiness_level,
               financial_profile, key_risk
        FROM readiness_history
        WHERE user_email = ?
        ORDER BY month
    """, (session["user"],))
    records = cursor.fetchall()
    conn.close()

    return render_template("history.html", records=records)
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors


@app.route("/download_history_pdf", methods=["GET", "POST"])
def download_history_pdf():
    if "user" not in session:
        return redirect("/login")

    conn = get_history_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT month, readiness_score, readiness_level,
               financial_profile, key_risk
        FROM readiness_history
        WHERE user_email = ?
        ORDER BY month
    """, (session["user"],))
    records = cursor.fetchall()
    conn.close()

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(
        "<b>Financial Readiness History Report</b>",
        styles["Title"]
    ))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(
        f"User: {session['user']}",
        styles["Normal"]
    ))
    elements.append(Spacer(1, 16))

    styles = getSampleStyleSheet()
    normal = styles["Normal"]
    table_data = [
    ["Month", "Score", "Level", "Profile", "Key Risk"]
]

    for r in records:
        table_data.append([
        r[0],  # Month
        f"{r[1]}/100",
        r[2],
        Paragraph(r[3], normal),  # ✅ wrapped Profile
        Paragraph(r[4], normal)   # ✅ wrapped Key Risk
    ])
    table = Table(
    table_data,
    colWidths=[70, 60, 60, 160, 180]  # balanced widths
    )
    table.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
    ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
    ("FONT", (0,0), (-1,0), "Helvetica-Bold"),
    ("VALIGN", (0,0), (-1,-1), "TOP"),
    ("LEFTPADDING", (0,0), (-1,-1), 6),
    ("RIGHTPADDING", (0,0), (-1,-1), 6),
]))
    
    elements.append(table)
    doc.build(elements)

    buffer.seek(0)
    return Response(
        buffer,
        mimetype="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=readiness_history.pdf"
        }
    )

# ---------- CLEAR HISTORY ----------
from flask import flash

@app.route("/clear_history", methods=["POST"])
def clear_history():
    if "user" not in session:
        return redirect("/login")

    conn = get_history_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM readiness_history
        WHERE user_email = ?
    """, (session["user"],))

    conn.commit()
    conn.close()

    # ✅ success message
    flash("History cleared successfully.", "success")

    return redirect("/history")



# ---------- ANALYZE ----------
@app.route("/analyze", methods=["POST"])
def analyze():
    if "user" not in session:
        return redirect("/login")

    income = float(request.form["income"])
    fixed = float(request.form["fixed_expenses"])
    variable = float(request.form["variable_expenses"])
    savings = float(request.form["intended_savings"])
    emergency = request.form["emergency_fund"]
    month = request.form["month"]

    # ---------- ❌ VALIDATION ----------
    errors = []

    if income <= 0:
        errors.append("Monthly income must be greater than zero.")

    if fixed < 0 or variable < 0 or savings < 0:
        errors.append("Expenses and savings cannot be negative.")

    if fixed + variable > income:
        errors.append(
            "Total expenses cannot exceed monthly income. "
            "Please correct your fixed or variable expenses."
        )

    if errors:
        # 🔁 fetch assessment count safely (FIX for Jinja error)
        conn = get_history_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM readiness_history
            WHERE user_email = ?
        """, (session["user"],))
        assessment_count = cursor.fetchone()[0]
        conn.close()

        return render_template(
            "dashboard.html",
            user=session["user"],
            errors=errors,
            assessment_count=assessment_count,
            last_score=None,
            trend="stable",
            trend_message="",
            next_action="",
            personal_message="",
            last_profile=None
        )

    # ---------- ✅ CONTINUE NORMAL FLOW ----------
    df = pd.DataFrame([{
        "month": month,
        "income": income,
        "fixed_expenses": fixed,
        "variable_expenses": variable,
        "intended_savings": savings,
        "actual_savings": income - fixed - variable,
        "emergency_fund": emergency
    }])

    df = calculate_metrics(df)
    df["readiness_score"] = df.apply(calculate_readiness_score, axis=1)
    df["readiness_level"] = df["readiness_score"].apply(classify_readiness)
    df["score_breakdown"] = df.apply(calculate_score_breakdown, axis=1)
    df["insights"] = df.apply(generate_insights, axis=1)
    df["resistance_reason"] = df.apply(detect_resistance, axis=1)

    save_web_plots(df)
    result = df.iloc[0]
    profile = determine_financial_profile(result)

    # ---------- 🧠 BEHAVIORAL MEMORY ----------
    behavior_memory = None
    conn = get_history_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT readiness_score, key_risk
        FROM readiness_history
        WHERE user_email = ?
        ORDER BY month DESC
        LIMIT 2
    """, (session["user"],))
    history = cursor.fetchall()

    if len(history) == 2:
        prev_score, prev_risk = history[1]
        curr_score = result["readiness_score"]

        if curr_score > prev_score:
            behavior_memory = (
                f"Last time you addressed '{prev_risk}', "
                f"your readiness score improved. "
                f"Repeating this behavior is likely to help again."
            )

    # ---------- SAVE HISTORY ----------
    cursor.execute("""
        INSERT INTO readiness_history (
            user_email,
            month,
            readiness_score,
            readiness_level,
            financial_profile,
            key_risk
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        session["user"],
        month,
        int(result["readiness_score"]),
        result["readiness_level"],
        profile,
        result["resistance_reason"]
    ))
    conn.commit()
    conn.close()

    return render_template(
        "result.html",
        score=result["readiness_score"],
        level=result["readiness_level"],
        resistance=result["resistance_reason"],
        insights=result["insights"],
        breakdown=result["score_breakdown"],
        what_if_results=simulate_multiple_reductions(result),
        financial_profile=profile,
        risk_flags=generate_risk_flags(result),
        report_text=generate_user_report(result),
        behavior_memory=behavior_memory
    )


# ---------- ABOUT ----------
@app.route("/about")
def about():
    return render_template("about.html")

# ---------- DOWNLOAD EVALUATION REPORT ----------
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from io import BytesIO


@app.route("/download_report", methods=["POST"])
def download_report():
    if "user" not in session:
        return redirect("/login")

    report_text = request.form.get("report_text", "")

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    elements.append(Paragraph(
        "<b>Financial Readiness Evaluation Report</b>",
        styles["Title"]
    ))
    elements.append(Spacer(1, 12))

    # User
    elements.append(Paragraph(
        f"<b>User:</b> {session['user']}",
        styles["Normal"]
    ))
    elements.append(Spacer(1, 12))

    # Body (split text into paragraphs)
    for line in report_text.split("\n"):
        elements.append(Paragraph(line, styles["Normal"]))
        elements.append(Spacer(1, 8))

    doc.build(elements)
    buffer.seek(0)

    return Response(
        buffer,
        mimetype="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=financial_readiness_report.pdf"
        }
    )




# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

