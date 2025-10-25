from sqlalchemy import select

from api_v1.auth.pwd import hash_password
from core.models import db_helper, User


async def create_admin():
    """
    Создаёт главного админа, если его ещё нет.
    """
    async with db_helper.session_factory() as session:
        exists = await session.execute(select(User).where(User.email == "admin@admin.com"))
        if not exists.scalar_one_or_none():
            admin = "admin"
            user = User(
                last_name=admin,
                first_name=admin,
                patronymic=admin,
                email=f"{admin}@{admin}.com",
                password=hash_password(f"{admin}{admin}"),
                is_superuser=True,
                is_active=True,
                permission_level=3,
            )
            session.add(user)
            await session.commit()
