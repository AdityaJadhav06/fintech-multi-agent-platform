from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.config import settings
from app.db.models import Base, Organization, User

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields an asynchronous database session.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    Initializes database schema and bootstraps default seed tenant.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed default organization and user for testing if absent
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select

        result = await session.execute(select(Organization).limit(1))
        existing_org = result.scalars().first()

        if not existing_org:
            default_org = Organization(
                id="ORG-DEFAULT-001",
                name="FinTech Bharat Global",
                subscription_tier="enterprise",
            )
            session.add(default_org)

            default_user = User(
                id="USER-DEFAULT-001",
                org_id=default_org.id,
                auth0_sub="auth0|student_dev_test_user",
                email="analyst@fintechbharat.com",
                role="admin",
            )
            session.add(default_user)
            await session.commit()
