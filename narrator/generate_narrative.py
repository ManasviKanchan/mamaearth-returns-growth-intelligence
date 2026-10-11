
"""
Mamaearth Returns & Growth Intelligence
Part 3: GenAI-Powered Insight Narrator

Gemini API + deterministic offline fallback
SCR: Situation - Complication - Resolution
"""

import json
import os
import re
from pathlib import Path

from google import genai
from google.genai import types


BASE_DIR = Path(__file__).resolve().parent
FINDINGS_PATH = BASE_DIR / "findings.json"
SAMPLE_PATH = BASE_DIR / "sample_output.txt"


def format_inr(value):
    """Format an INR amount to two decimal places."""
    return f"{float(value):,.2f}"


def generate_scr_narrative_offline(findings: dict) -> dict:
    """Generate a deterministic SCR report without API access."""

    cleaned = format_inr(findings["cleaned_total_revenue_inr"])
    raw = format_inr(findings["raw_total_revenue_inr"])
    delta = format_inr(
        findings["duplicate_reconciliation_delta_inr"]
    )

    rates = findings["return_rate_by_payment"]
    risk = findings["highest_risk_segment"]
    peak = findings["true_peak_month"]
    inflated = findings["outlier_inflated_month"]

    peak_month = __import__("datetime").datetime.strptime(
        peak["month"], "%Y-%m"
    ).strftime("%B %Y")

    narrative = f"""Situation
Mamaearth's cleaned order data records total revenue of INR {cleaned}, compared with raw revenue of INR {raw}. After excluding the identified quantity outliers from the monthly trend, {peak_month} is the true peak month, with revenue of INR {format_inr(peak["revenue_inr"])}.

Complication
Duplicate orders account for a reconciliation difference of INR {delta} between raw and cleaned revenue. Returns also vary across payment methods: COD has a return rate of {rates["COD"]:.1f}%, compared with {rates["CARD"]:.1f}% for CARD and {rates["UPI"]:.1f}% for UPI. The highest-risk observed segment is {risk["payment_method"]} in Tier-{risk["city_tier"]} cities, with a {risk["return_rate_pct"]:.1f}% return rate. January's apparent revenue of INR {format_inr(inflated["apparent_revenue_inr"])} falls to INR {format_inr(inflated["corrected_revenue_inr"])} when quantity outliers are excluded from the monthly trend.

Resolution
Mamaearth should prioritize reviewing COD return patterns, especially in Tier-{risk["city_tier"]} cities, and investigate possible operational causes before changing policy. Finance teams should reconcile duplicates before reporting revenue and compare monthly performance with and without flagged quantity outliers. These actions can improve reporting reliability and help operations teams target further investigation. The observed associations do not, by themselves, establish causation."""

    return {
        "status": "success",
        "narrative": narrative,
        "tokens": 0,
    }


def generate_scr_narrative(findings: dict) -> dict:
    """Use Gemini when configured; otherwise use offline SCR."""

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print("No Gemini API key: using offline fallback.")
        return generate_scr_narrative_offline(findings)

    system_instruction = (
        "You are a senior data analyst writing for Mamaearth's "
        "regional ops and finance heads. Write a factual business "
        "narrative with exactly three labeled sections: Situation, "
        "Complication, and Resolution. Every number in the output "
        "must come from the supplied findings and appear with the "
        "same value; do not invent statistics. Preserve the "
        "difference between raw revenue, cleaned revenue, and "
        "outlier-corrected monthly revenue. Explain that observed "
        "associations do not prove causation. Include all verified "
        "revenue, return-rate, risk-segment, and peak-month findings."
    )

    # The prompt is built from the argument, not fixed numbers.
    user_prompt = (
        "Write an approximately 250-word SCR business report "
        "using only these verified findings:\n"
        + json.dumps(findings, indent=2)
    )

    try:
        client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(timeout=30000),
        )

        response = client.models.generate_content(
            model="gemini-flash-lite-latest",
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                # Temperature 0 minimizes creative variation
                # in a factual business report.
                temperature=0.0,
                max_output_tokens=1200,
            ),
        )

        narrative = response.text

        if not narrative:
            raise ValueError("Gemini returned an empty narrative.")

        tokens = None
        if response.usage_metadata:
            tokens = response.usage_metadata.total_token_count

        return {
            "status": "success",
            "narrative": narrative,
            "tokens": tokens,
        }

    except Exception as err:
        # Keep the structured API error for diagnostics.
        error_result = {
            "status": "error",
            "narrative": None,
            "message": str(err),
        }
        print("Gemini API error:", error_result["message"])
        print("Switching to offline fallback.")

        return generate_scr_narrative_offline(findings)


def check_numeric_accuracy(narrative: str, findings: dict) -> bool:
    """Print a PASS/FAIL line for each required figure."""

    if not narrative:
        print("FAIL: Narrative is empty.")
        return False

    # Remove commas so 97,358.30 and 97358.30 match.
    normalized = narrative.replace(",", "")

    def contains_number(value):
        # Accept two-decimal formatting or equivalent rounding.
        number = f"{float(value):.2f}".rstrip("0").rstrip(".")
        pattern = (
            r"(?<![\d.])"
            + re.escape(number)
            + r"(?:0+)?(?!\d)"
        )
        return bool(re.search(pattern, normalized))

    peak = findings["true_peak_month"]
    peak_name = __import__("datetime").datetime.strptime(
        peak["month"], "%Y-%m"
    ).strftime("%B")

    checks = {
        "Cleaned revenue": contains_number(
            findings["cleaned_total_revenue_inr"]
        ),
        "COD return rate": contains_number(
            findings["return_rate_by_payment"]["COD"]
        ),
        "COD Tier-2 risk rate": contains_number(
            findings["highest_risk_segment"]["return_rate_pct"]
        ),
        "Duplicate reconciliation": contains_number(
            findings["duplicate_reconciliation_delta_inr"]
        ),
        "True peak month and revenue": (
            peak_name.lower() in normalized.lower()
            and contains_number(peak["revenue_inr"])
        ),
    }

    for label, passed in checks.items():
        print(f'{"PASS" if passed else "FAIL"}: {label}')

    return all(checks.values())


def main():
    with open(FINDINGS_PATH, "r", encoding="utf-8") as file:
        findings = json.load(file)

    result = generate_scr_narrative(findings)

    print("\n=== SCR NARRATIVE ===\n")
    print(result["narrative"])

    print("\n=== NUMERIC ACCURACY CHECK ===")
    valid = check_numeric_accuracy(result["narrative"], findings)

    # If Gemini omits a required number, use the verified
    # offline template rather than saving an inaccurate sample.
    if not valid:
        print("\nUsing offline narrative to ensure accuracy.")
        result = generate_scr_narrative_offline(findings)
        valid = check_numeric_accuracy(result["narrative"], findings)

    if not valid:
        raise RuntimeError("Narrative failed numeric checks.")

    SAMPLE_PATH.write_text(
        result["narrative"], encoding="utf-8"
    )

    print(f"\nSaved sample to: {SAMPLE_PATH}")
    print("All five numeric accuracy checks passed.")


if __name__ == "__main__":
    main()
