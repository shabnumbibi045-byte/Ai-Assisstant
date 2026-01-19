"""
Verify and add research permissions to all users.
Ensures users can access legal research tools via CourtListener API.
"""

import asyncio
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Database configuration from .env
DATABASE_URL = "mysql+pymysql://root:root@localhost:3306/salim_ai"

def verify_and_add_permissions():
    """Verify research permissions and add if missing."""

    # Create synchronous engine for simple operations
    engine = create_engine(DATABASE_URL, echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        print("=" * 60)
        print("RESEARCH PERMISSIONS VERIFICATION")
        print("=" * 60)
        print()

        # Get all users (use id, not user_id for permissions table)
        users_query = text("SELECT id, email FROM users")
        users = session.execute(users_query).fetchall()

        print(f"Found {len(users)} users")
        print()

        # Research permission types to ensure exist
        research_perms = [
            ("research", "read"),
            ("research", "write")
        ]

        added_count = 0
        already_exists_count = 0

        for user_id_int, email in users:
            print(f"Checking permissions for: {email}")

            for module, perm_type in research_perms:
                # Check if permission exists
                check_query = text("""
                    SELECT COUNT(*) as count
                    FROM user_permissions
                    WHERE user_id = :user_id AND module = :module AND permission_type = :perm_type
                """)

                result = session.execute(
                    check_query,
                    {"user_id": user_id_int, "module": module, "perm_type": perm_type}
                ).fetchone()

                if result.count == 0:
                    # Add permission
                    insert_query = text("""
                        INSERT INTO user_permissions (user_id, module, permission_type, granted)
                        VALUES (:user_id, :module, :perm_type, 1)
                    """)
                    session.execute(
                        insert_query,
                        {"user_id": user_id_int, "module": module, "perm_type": perm_type}
                    )
                    print(f"  ✅ Added: {module}_{perm_type}")
                    added_count += 1
                else:
                    print(f"  ✓ Already has: {module}_{perm_type}")
                    already_exists_count += 1

            print()

        session.commit()

        print("=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"✅ Permissions added: {added_count}")
        print(f"✓  Already existed: {already_exists_count}")
        print(f"👥 Users processed: {len(users)}")
        print()

        # Show current research permissions
        print("=" * 60)
        print("CURRENT RESEARCH PERMISSIONS")
        print("=" * 60)

        perms_query = text("""
            SELECT u.email, up.module, up.permission_type, up.granted
            FROM users u
            JOIN user_permissions up ON u.user_id = up.user_id
            WHERE up.module = 'research'
            ORDER BY u.email, up.permission_type
        """)

        perms = session.execute(perms_query).fetchall()

        current_user = None
        for email, module, perm_type, granted in perms:
            if email != current_user:
                print(f"\n{email}:")
                current_user = email
            status = "✅" if granted else "❌"
            print(f"  {status} {module}_{perm_type}")

        print()
        print("=" * 60)
        print("✅ Research permissions verification complete!")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        session.rollback()
        return False
    finally:
        session.close()


if __name__ == "__main__":
    success = verify_and_add_permissions()
    sys.exit(0 if success else 1)
