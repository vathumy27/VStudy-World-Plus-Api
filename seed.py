"""
Run database seeders.

Usage (from API project root):
  export FLASK_APP=run.py
  python seed.py
  python seed.py --reset-admin-password
  python seed.py --generate-study-resources
"""

import argparse
import sys

from app import create_app
from app.seeders.admin_seeder import seed_admin
from app.seeders.content_seeder import seed_sample_content
from app.seeders.ethaksalawa_seeder import import_ethaksalawa_grade_10_11
from app.seeders.study_resource_seeder import seed_study_resources


def main():
    parser = argparse.ArgumentParser(description="Seed VStudy World Plus data")
    parser.add_argument(
        "--reset-admin-password",
        action="store_true",
        help="Reset admin password to admin123 even if the user already exists",
    )
    parser.add_argument(
        "--import-ethaksalawa",
        action="store_true",
        help="Import official Grade 10/11 lesson topics from e-Thaksalawa (metadata only)",
    )
    parser.add_argument(
        "--generate-study-resources",
        action="store_true",
        help="Generate and store original AI study notes / Math resource packs",
    )
    parser.add_argument(
        "--regenerate-study-resources",
        action="store_true",
        help="Force regenerate study resources even if they already exist",
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

        content = seed_sample_content()
        print(
            f"[seed] Content: +{content['subjects_created']} subjects, "
            f"+{content['lessons_created']} lessons "
            f"(total {content['subjects_total']} subjects / {content['lessons_total']} lessons)"
        )

        if args.import_ethaksalawa:
            result = import_ethaksalawa_grade_10_11()
            print(
                "[seed] e-Thaksalawa: "
                f"+{result['lessons_created']} created, "
                f"{result['lessons_updated']} updated, "
                f"courses={result['courses_processed']}, errors={len(result['errors'])}"
            )
            for err in result["errors"][:10]:
                print(f"[seed][warn] {err}")

        if args.generate_study_resources or args.regenerate_study_resources:
            stats = seed_study_resources(
                regenerate=args.regenerate_study_resources
            )
            print(
                "[seed] Study resources: "
                f"notes_created={stats['lesson_notes_created']}, "
                f"notes_skipped={stats['lesson_notes_skipped']}, "
                f"math_packs={stats['math_resources']}, "
                f"errors={len(stats['errors'])}"
            )
            for err in stats["errors"][:10]:
                print(f"[seed][warn] {err}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
