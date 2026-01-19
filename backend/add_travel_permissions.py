"""
Script to add travel module permissions to all existing users.
Run this to enable travel module for users who were created before travel integration.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import select
from datetime import datetime
from app.database.database import db_manager
from app.database.models import User, UserPermission


async def add_travel_permissions():
    """Add travel module permissions to all users."""
    async with db_manager.async_session_maker() as db:
        try:
            # Get all users
            stmt = select(User)
            result = await db.execute(stmt)
            users = result.scalars().all()

            print(f"Found {len(users)} users")

            added_count = 0
            skipped_count = 0

            for user in users:
                # Check if user already has travel permission
                perm_stmt = select(UserPermission).where(
                    UserPermission.user_id == user.id,
                    UserPermission.module == "travel"
                )
                perm_result = await db.execute(perm_stmt)
                existing_perm = perm_result.scalar_one_or_none()

                if existing_perm:
                    print(f"  ✓ User {user.email} already has travel permission")
                    skipped_count += 1
                    continue

                # Add travel permission
                travel_permission = UserPermission(
                    user_id=user.id,
                    module="travel",
                    permission_type="read",
                    granted=True,
                    granted_at=datetime.utcnow()
                )
                db.add(travel_permission)

                # Also add banking and stocks if they don't exist
                for module in ["banking", "stocks", "research"]:
                    mod_perm_stmt = select(UserPermission).where(
                        UserPermission.user_id == user.id,
                        UserPermission.module == module
                    )
                    mod_perm_result = await db.execute(mod_perm_stmt)
                    mod_existing_perm = mod_perm_result.scalar_one_or_none()

                    if not mod_existing_perm:
                        new_permission = UserPermission(
                            user_id=user.id,
                            module=module,
                            permission_type="read",
                            granted=True,
                            granted_at=datetime.utcnow()
                        )
                        db.add(new_permission)
                        print(f"  + Added {module} permission for {user.email}")

                print(f"  + Added travel permission for {user.email}")
                added_count += 1

            await db.commit()

            print(f"\n✅ Complete!")
            print(f"   Added permissions for {added_count} users")
            print(f"   Skipped {skipped_count} users (already had travel permission)")

        except Exception as e:
            print(f"❌ Error: {e}")
            await db.rollback()
            raise


async def main():
    """Main entry point."""
    print("=" * 60)
    print("Adding Travel Module Permissions to Existing Users")
    print("=" * 60)
    print()

    try:
        await add_travel_permissions()
        print("\nAll users now have travel module access! 🎉")
    except Exception as e:
        print(f"\nFailed to add permissions: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
