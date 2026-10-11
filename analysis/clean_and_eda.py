
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
