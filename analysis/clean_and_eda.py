
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
