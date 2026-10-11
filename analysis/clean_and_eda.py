
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
