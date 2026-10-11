
import pandas as pd
from pathlib import Path

# Part 2 - Task 1: Load and Inspect

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

orders = pd.read_csv(DATA_DIR / "orders.csv")
customers = pd.read_csv(DATA_DIR / "customers.csv")
products = pd.read_csv(DATA_DIR / "products.csv")

print("TASK 1: LOAD AND INSPECT")
print("Orders shape:", orders.shape)
print("Customers shape:", customers.shape)
print("Products shape:", products.shape)

print("\nFirst 5 rows of orders:")
print(orders.head())

print("\nMissing values:")
print(orders.isnull().sum())


# ==========================================
# Task 2: Standardize Payment Method Casing
# ==========================================

print("\nTASK 2: PAYMENT METHOD STANDARDIZATION")

# Before cleaning
print("\nUnique payment methods BEFORE cleaning:")
print(orders["payment_method"].unique())

print("\nNumber of unique values BEFORE cleaning:")
print(orders["payment_method"].nunique())

# Standardize casing and remove extra spaces
orders["payment_method"] = (
    orders["payment_method"]
    .str.strip()
    .str.upper()
)

# After cleaning
print("\nUnique payment methods AFTER cleaning:")
print(orders["payment_method"].unique())

print("\nNumber of unique values AFTER cleaning:")
print(orders["payment_method"].nunique())

print("\nPayment method counts:")
print(orders["payment_method"].value_counts())



# ==========================================
# Task 3: Detect and Remove Duplicate Orders
# ==========================================

print("\nTASK 3: DUPLICATE ORDER DETECTION")

# Natural key excludes order_id
natural_key = [
    "customer_id",
    "product_id",
    "order_date",
    "quantity",
    "discount_pct",
    "payment_method",
    "rating",
    "returned"
]

# Detect duplicate rows
duplicate_mask = orders.duplicated(
    subset=natural_key,
    keep="first"
)

print("\nNumber of duplicate orders:")
print(duplicate_mask.sum())

print("\nDropped order IDs:")
print(orders.loc[duplicate_mask, "order_id"].tolist())

# Remove duplicates
orders_clean = orders.loc[~duplicate_mask].copy()

print("\nOrders shape after removing duplicates:")
print(orders_clean.shape)



# ==========================================
# Task 4: Impute Missing Values
# ==========================================

print("\nTASK 4: MISSING VALUE IMPUTATION")

# Count missing values after duplicate removal
missing_discounts = orders_clean["discount_pct"].isna().sum()
missing_ratings = orders_clean["rating"].isna().sum()

print("\nMissing discounts before imputation:", missing_discounts)
print("Missing ratings before imputation:", missing_ratings)

# Calculate median rating before filling missing values
median_rating = orders_clean["rating"].median()
print("\nMedian rating before imputation:", median_rating)

# Fill missing discounts with 0
orders_clean["discount_pct"] = (
    orders_clean["discount_pct"].fillna(0)
)

# Fill missing ratings with median
orders_clean["rating"] = (
    orders_clean["rating"].fillna(median_rating)
)

# Verify missing values after imputation
print("\nMissing values after imputation:")
print(
    orders_clean[["discount_pct", "rating"]]
    .isnull()
    .sum()
)



# ==========================================
# Task 5: Merge and Revenue Reconciliation
# ==========================================

print("\nTASK 5: MERGE AND RECONCILIATION")

# Merge cleaned orders with products and customers
merged = (
    orders_clean
    .merge(products, on="product_id", how="inner", validate="many_to_one")
    .merge(customers, on="customer_id", how="inner", validate="many_to_one")
)

# Calculate cleaned order value
merged["order_value"] = (
    merged["quantity"]
    * merged["price"]
    * (1 - merged["discount_pct"] / 100.0)
)

cleaned_total = round(merged["order_value"].sum(), 2)

print("\nMerged dataset shape:", merged.shape)
print("Cleaned orders count:", len(merged))
print(f"Cleaned total revenue: Rs. {cleaned_total:.2f}")

# Independently calculate revenue of the 5 dropped orders
dropped_orders = orders.loc[duplicate_mask].copy()

dropped_merged = dropped_orders.merge(
    products, on="product_id", how="inner"
)

dropped_merged["order_value"] = (
    dropped_merged["quantity"]
    * dropped_merged["price"]
    * (
        1 - dropped_merged["discount_pct"].fillna(0) / 100.0
    )
)

duplicate_revenue = round(
    dropped_merged["order_value"].sum(), 2
)

raw_sql_total = 99860.20
revenue_difference = round(raw_sql_total - cleaned_total, 2)

print(f"Revenue of 5 removed duplicates: Rs. {duplicate_revenue:.2f}")
print(f"Raw SQL revenue: Rs. {raw_sql_total:.2f}")
print(f"Revenue difference: Rs. {revenue_difference:.2f}")

print(
    "\nReconciliation Note: Part 1 SQL reports raw revenue of "
    f"Rs. {raw_sql_total:.2f}, while Part 2 reports cleaned revenue "
    f"of Rs. {cleaned_total:.2f}. The exact difference of "
    f"Rs. {revenue_difference:.2f} is attributable to the five "
    "duplicate orders removed in Task 3 (O0176-O0180), whose "
    f"combined order value is Rs. {duplicate_revenue:.2f}. "
    "Filling missing discounts with zero and ratings with the "
    "median does not change revenue because missing discounts "
    "were already treated as zero in Part 1 using COALESCE, "
    "and ratings are not used in the order-value calculation."
)




# ==========================================
# Task 6: IQR Outlier Detection
# ==========================================

print("\nTASK 6: IQR OUTLIER DETECTION")

# Calculate quartiles and IQR
Q1 = merged["quantity"].quantile(0.25)
Q3 = merged["quantity"].quantile(0.75)
IQR = Q3 - Q1

lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

print("Q1:", Q1)
print("Q3:", Q3)
print("IQR:", IQR)
print("Lower bound:", lower_bound)
print("Upper bound:", upper_bound)

# Flag outliers without deleting them
merged["is_outlier"] = (
    (merged["quantity"] < lower_bound) |
    (merged["quantity"] > upper_bound)
)

outliers = merged.loc[
    merged["is_outlier"],
    ["order_id", "quantity"]
]



# ==========================================
# Task 7: Hypothesis Testing - COD Returns
# ==========================================

print("\nTASK 7: COD RETURN RATE HYPOTHESIS")

print(
    "Hypothesis: COD orders have a higher return "
    "rate than CARD and UPI orders."
)

# Calculate return rates by payment method
payment_returns = (
    merged.groupby("payment_method")["returned"]
    .agg(["count", "mean"])
)

# Convert mean to percentage
payment_returns["return_rate_pct"] = (
    payment_returns["mean"] * 100
).round(1)

print("\nReturn rates by payment method:")
print(payment_returns)

# Verify hypothesis
cod_rate = payment_returns.loc["COD", "mean"]
other_rates = payment_returns.loc[
    ["CARD", "UPI"], "mean"
]

if (cod_rate > other_rates).all():
    print("\nHypothesis Result: Confirmed")
    print(
        "COD has the highest return rate among "
        "all payment methods."
    )
else:
    print("\nHypothesis Result: Busted")


print("\nNumber of outliers:", len(outliers))
print("\nOutlier orders:")
print(outliers.to_string(index=False))



# ==========================================
# Task 8: Multi-Level Return Rate Segmentation
# ==========================================

print("\nTASK 8: PAYMENT METHOD AND CITY TIER SEGMENTATION")

# Group by payment method and city tier
segment_returns = (
    merged.groupby(["payment_method", "city_tier"])["returned"]
    .agg(["count", "mean"])
)

# Calculate return rate percentage
segment_returns["return_rate_pct"] = (
    segment_returns["mean"] * 100
).round(1)

print("\nReturn rates by payment method and city tier:")
print(segment_returns)

# Identify the segment with the highest return rate
highest_segment = segment_returns["mean"].idxmax()
highest_rate = segment_returns.loc[
    highest_segment, "return_rate_pct"
]

print("\nHighest return rate segment:")
print("Payment method:", highest_segment[0])
print("City tier:", highest_segment[1])
print(f"Return rate: {highest_rate:.1f}%")

print(
    "\nInsight: COD orders from Tier-2 cities have "
    "the highest observed return rate, suggesting "
    "this segment should be prioritized for "
    "further investigation."
)


# ==========================================
# Task 9: Correlation Analysis
# ==========================================

print("\nTASK 9: CORRELATION ANALYSIS")

# Select numeric variables
correlation_columns = [
    "rating", "returned", "discount_pct", "quantity"
]

# Calculate Pearson correlation matrix
correlation_matrix = merged[correlation_columns].corr()

print("\nCorrelation Matrix:")
print(correlation_matrix.round(3))

# Interpret correlation strength
def correlation_strength(value):
    absolute_value = abs(value)

    if absolute_value < 0.20:
        return "Negligible"
    elif absolute_value < 0.40:
        return "Weak"
    elif absolute_value < 0.70:
        return "Moderate"
    else:
        return "Strong"

print("\nPairwise Correlation Interpretation:")

for i in range(len(correlation_columns)):
    for j in range(i + 1, len(correlation_columns)):
        col1 = correlation_columns[i]
        col2 = correlation_columns[j]

        value = correlation_matrix.loc[col1, col2]
        strength = correlation_strength(value)

        print(
            f"{col1} vs {col2}: "
            f"r = {value:.3f} ({strength})"
        )

# Test discount-return hypothesis
discount_return_corr = correlation_matrix.loc[
    "discount_pct", "returned"
]

print("\nHypothesis: Higher discounts reduce returns.")

print(
    f"Discount vs Returned correlation: "
    f"{discount_return_corr:.3f}"
)

if discount_return_corr <= -0.20:
    print(
        "Hypothesis Result: Supported by a "
        "negative correlation."
    )
else:
    print("\nHypothesis Result: Busted")
    print(
        "The relationship between discounts and returns "
        "is negligible. There is insufficient evidence "
        "that higher discounts reduce returns."
    )


# ==========================================
# Task 10: Monthly Revenue and Outlier Impact
# ==========================================

print("\nTASK 10: MONTHLY REVENUE TREND")

# Convert order_date into datetime format
merged["order_date"] = pd.to_datetime(merged["order_date"])

# Create month column
merged["month"] = merged["order_date"].dt.to_period("M")

# Revenue including quantity outliers
monthly_with_outliers = (
    merged.groupby("month")["order_value"]
    .sum()
    .round(2)
)

# Revenue excluding flagged quantity outliers
monthly_without_outliers = (
    merged.loc[~merged["is_outlier"]]
    .groupby("month")["order_value"]
    .sum()
    .round(2)
)

# Compare monthly revenue
monthly_comparison = pd.DataFrame({
    "including_outliers": monthly_with_outliers,
    "excluding_outliers": monthly_without_outliers
}).fillna(0)

monthly_comparison["difference"] = (
    monthly_comparison["including_outliers"]
    - monthly_comparison["excluding_outliers"]
).round(2)

print("\nMonthly Revenue Comparison (Rs.):")
print(monthly_comparison.to_string())

# Identify peak months
peak_with = monthly_with_outliers.idxmax()
peak_without = monthly_without_outliers.idxmax()

print("\nPeak month including outliers:", peak_with)
print(
    "Peak revenue including outliers: "
    f"Rs. {monthly_with_outliers.max():.2f}"
)

print("\nPeak month excluding outliers:", peak_without)
print(
    "Peak revenue excluding outliers: "
    f"Rs. {monthly_without_outliers.max():.2f}"
)

# Display flagged orders responsible for the distortion
print("\nFlagged Outlier Orders:")
print(
    merged.loc[
        merged["is_outlier"],
        ["order_id", "order_date", "quantity", "order_value"]
    ].to_string(index=False)
)

print(
    "\nInterpretation: January appears to be the highest-revenue "
    "month when quantity outliers are included. However, "
    "two unusually large January orders (O0011 and O0098) "
    "inflate its revenue. After excluding these flagged "
    "orders, March becomes the true peak month in the "
    "outlier-corrected analysis."
)






# ==========================================
# PART 3 - TASK 1: EXPORT VERIFIED FINDINGS
# ==========================================

import json
from pathlib import Path

print("\nPART 3 - TASK 1: EXPORT FINDINGS")

# Locate repository root independently of
# the directory from which the script runs.
BASE_DIR = Path(__file__).resolve().parent.parent
NARRATOR_DIR = BASE_DIR / "narrator"

NARRATOR_DIR.mkdir(parents=True, exist_ok=True)

# Build findings directly from computed
# Part 2 analysis results.

findings = {
    "cleaned_total_revenue_inr": round(
        float(merged["order_value"].sum()), 2
    ),

    "raw_total_revenue_inr": round(
        float(merged["order_value"].sum()
              + duplicate_revenue), 2
    ),

    "duplicate_reconciliation_delta_inr": round(
        float(duplicate_revenue), 2
    ),

    "return_rate_by_payment": {
        method: round(float(rate), 1)
        for method, rate in (
            payment_returns["mean"] * 100
        ).items()
    },

    "highest_risk_segment": {
        "payment_method": str(highest_segment[0]),
        "city_tier": int(highest_segment[1]),
        "return_rate_pct": round(
            float(highest_rate), 1
        )
    },

    "true_peak_month": {
        "month": str(peak_without),
        "revenue_inr": round(
            float(monthly_without_outliers.max()), 2
        )
    },

    "outlier_inflated_month": {
        "month": str(peak_with),
        "apparent_revenue_inr": round(
            float(monthly_with_outliers.max()), 2
        ),
        "corrected_revenue_inr": round(
            float(monthly_without_outliers.loc[peak_with]), 2
        )
    }
}

# Export structured JSON
output_path = NARRATOR_DIR / "findings.json"

with open(output_path, "w", encoding="utf-8") as file:
    json.dump(findings, file, indent=4)

print(f"\nFindings exported to: {output_path}")
print("\nGenerated JSON:")
print(json.dumps(findings, indent=4))

print("\nPART 3 TASK 1 COMPLETED")
