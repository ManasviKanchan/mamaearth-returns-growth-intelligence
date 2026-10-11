
# ==========================================
# Task 11: Mamaearth Data Visualizations
# ==========================================

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
VIS_DIR = BASE_DIR / "visualizations"

VIS_DIR.mkdir(parents=True, exist_ok=True)

# Load raw datasets
orders = pd.read_csv(DATA_DIR / "orders.csv")
products = pd.read_csv(DATA_DIR / "products.csv")

# Standardize payment methods
orders["payment_method"] = (
    orders["payment_method"].str.strip().str.upper()
)

# Remove duplicate orders using natural key
natural_key = [
    "customer_id", "product_id", "order_date",
    "quantity", "discount_pct", "payment_method",
    "rating", "returned"
]

orders_clean = orders.loc[
    ~orders.duplicated(subset=natural_key, keep="first")
].copy()

# Impute missing values
orders_clean["discount_pct"] = (
    orders_clean["discount_pct"].fillna(0)
)

orders_clean["rating"] = (
    orders_clean["rating"].fillna(
        orders_clean["rating"].median()
    )
)

# ==========================================
# Chart 1: Return Rate by Payment Method
# ==========================================

payment_returns = (
    orders_clean.groupby("payment_method")["returned"]
    .mean()
    .mul(100)
    .sort_values(ascending=False)
)

fig, ax = plt.subplots(figsize=(9, 5))

bars = ax.bar(
    payment_returns.index,
    payment_returns.values,
    color=["#D65A50", "#E9A23B", "#5796B3"]
)

for bar, value in zip(bars, payment_returns.values):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 1,
        f"{value:.1f}%",
        ha="center",
        fontsize=11,
        fontweight="bold"
    )

ax.set_title(
    "COD Returns at 44.4% — 3x Card",
    fontsize=15,
    fontweight="bold"
)
ax.set_xlabel("Payment Method")
ax.set_ylabel("Return Rate (%)")
ax.set_ylim(0, 55)
ax.grid(axis="y", alpha=0.2)

plt.tight_layout()
plt.savefig(
    VIS_DIR / "return_rate_by_payment.png",
    dpi=300,
    bbox_inches="tight"
)
plt.close()

print("Saved: visualizations/return_rate_by_payment.png")

# ==========================================
# Chart 2: Outlier-Corrected Monthly Revenue
# ==========================================

# Merge orders with product prices
merged = orders_clean.merge(
    products,
    on="product_id",
    how="inner",
    validate="many_to_one"
)

# Calculate order value
merged["order_value"] = (
    merged["quantity"]
    * merged["price"]
    * (1 - merged["discount_pct"] / 100)
)

# Detect quantity outliers using IQR
Q1 = merged["quantity"].quantile(0.25)
Q3 = merged["quantity"].quantile(0.75)
IQR = Q3 - Q1

lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

merged["is_outlier"] = (
    (merged["quantity"] < lower_bound)
    | (merged["quantity"] > upper_bound)
)

# Exclude outliers from corrected trend
corrected_orders = merged.loc[
    ~merged["is_outlier"]
].copy()

corrected_orders["order_date"] = pd.to_datetime(
    corrected_orders["order_date"]
)

corrected_orders["month"] = (
    corrected_orders["order_date"].dt.to_period("M")
)

monthly_revenue = (
    corrected_orders.groupby("month")["order_value"]
    .sum()
    .sort_index()
)

month_labels = monthly_revenue.index.strftime("%b %Y")

fig, ax = plt.subplots(figsize=(10, 5))

ax.plot(
    month_labels,
    monthly_revenue.values,
    marker="o",
    linewidth=2.5,
    color="#247B78"
)

for month, revenue in zip(
    month_labels,
    monthly_revenue.values
):
    ax.annotate(
        f"Rs. {revenue:,.0f}",
        (month, revenue),
        textcoords="offset points",
        xytext=(0, 10),
        ha="center",
        fontsize=9
    )

ax.set_title(
    "March Leads Revenue After Removing Quantity Outliers",
    fontsize=14,
    fontweight="bold"
)
ax.set_xlabel("Month")
ax.set_ylabel("Revenue (Rs.)")
ax.grid(alpha=0.2)

plt.tight_layout()
plt.savefig(
    VIS_DIR / "monthly_revenue_trend.png",
    dpi=300,
    bbox_inches="tight"
)
plt.close()

print("Saved: visualizations/monthly_revenue_trend.png")

print("\nTASK 11 COMPLETED")
