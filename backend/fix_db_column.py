import sys
import os

# Ensure backend directory is in path if needed, though running from /app often suffices
sys.path.append("/app")

from sqlalchemy import text
from models.database import engine


def add_column():
    with engine.connect() as connection:
        try:
            print("Attempting to add 'profile_picture' column to 'users' table...")
            connection.execute(
                text("ALTER TABLE users ADD COLUMN profile_picture VARCHAR(500) NULL;")
            )
            connection.commit()
            print("Successfully added 'profile_picture' column.")
        except Exception as e:
            print(f"Error (might already exist): {e}")


if __name__ == "__main__":
    add_column()
