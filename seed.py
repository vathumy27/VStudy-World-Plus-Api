"""
Run database seeders.

Usage (from API project root):
  export FLASK_APP=run.py
  python seed.py
  python seed.py --reset-admin-password
"""

import argparse
import sys

from app import create_app
from app.seeders.admin_seeder import seed_admin


def main():
    parser = argparse.ArgumentParser(description="Seed VStudy World Plus data")
    parser.add_argument(
        "--reset-admin-password",
        action="store_true",
        help="Reset admin password to admin123 even if the user already exists",
    )
    args = parser.parse_args()

    app = create_app()
    with app.app_context():
        result = seed_admin(force_password=args.reset_admin_password)
        print(
            f"[seed] Admin {result['action']}: "
            f"{result['email']} (id={result['id']}, role={result['role']})"
        )
        if result["action"] == "created" or args.reset_admin_password:
            print("[seed] Login with admin@gmail.com / admin123")
    return 0


if __name__ == "__main__":
    sys.exit(main())
