
import sqlite3
from pathlib import Path

import pandas as pd

# Locate the repository automatically
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
SCHEMA_PATH = BASE_DIR / "sql" / "schema.sql"
DATABASE_PATH = BASE_DIR / "mamaearth.db"


def main():
    # Rebuild the database from the original CSV files
    if DATABASE_PATH.exists():
        DATABASE_PATH.unlink()

    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON")

        # Create database tables
        conn.executescript(
            SCHEMA_PATH.read_text(encoding="utf-8")
        )

        # Import original data without removing duplicates
        for table in ["customers", "products", "orders"]:
            csv_path = DATA_DIR / f"{table}.csv"
            df = pd.read_csv(csv_path)

            df.to_sql(
                table,
                conn,
                if_exists="append",
                index=False
            )

            print(f"{table}: {len(df)} rows imported")

        # Validate foreign-key relationships
        violations = conn.execute(
            "PRAGMA foreign_key_check"
        ).fetchall()

        if violations:
            raise RuntimeError(
                f"Foreign-key violations: {violations}"
            )

        print("Foreign-key validation: PASS")

    print(f"Database created: {DATABASE_PATH}")


if __name__ == "__main__":
    main()
