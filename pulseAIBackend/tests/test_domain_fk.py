import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.domain import Base, Employee, EngagementSnapshot, Alert, AlertRecipientState
import pytest_asyncio

# Setup test DB (SQLite in-memory async)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture(scope="function")
async def db_session():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
        
    await engine.dispose()

@pytest.mark.asyncio
async def test_employee_engagement_cascade(db_session: AsyncSession):
    # Create employee
    emp = Employee(
        id="emp-1",
        first_name="Test",
        last_name="User",
        email="test@example.com",
        status="actif"
    )
    db_session.add(emp)
    await db_session.commit()
    
    # Create engagement snapshot linked to employee
    snapshot = EngagementSnapshot(
        id="snap-1",
        employee_id="emp-1",
        score=85,
        source_signals={"q1": 5}
    )
    db_session.add(snapshot)
    await db_session.commit()
    
    # Verify snapshot exists
    from sqlalchemy import select
    res = await db_session.execute(select(EngagementSnapshot).where(EngagementSnapshot.employee_id == "emp-1"))
    assert len(res.scalars().all()) == 1
    
    # Delete employee
    await db_session.delete(emp)
    await db_session.commit()
    
    # Verify snapshot is deleted (cascade)
    res = await db_session.execute(select(EngagementSnapshot).where(EngagementSnapshot.employee_id == "emp-1"))
    assert len(res.scalars().all()) == 0

@pytest.mark.asyncio
async def test_alert_recipient_state_cascade(db_session: AsyncSession):
    alert = Alert(
        id="alert-1",
        fingerprint="test-alert-1",
        type="risk",
        severity="high",
        title="Risk high",
        employee_id="emp-1"
    )
    db_session.add(alert)
    await db_session.commit()
    
    recipient = AlertRecipientState(
        id="rec-1",
        alert_id="alert-1",
        user_id="manager-1",
        status="unread"
    )
    db_session.add(recipient)
    await db_session.commit()
    
    # Verify recipient exists
    from sqlalchemy import select
    res = await db_session.execute(select(AlertRecipientState).where(AlertRecipientState.alert_id == "alert-1"))
    assert len(res.scalars().all()) == 1
    
    # Delete alert
    await db_session.delete(alert)
    await db_session.commit()
    
    # Verify recipient state is deleted (cascade)
    res = await db_session.execute(select(AlertRecipientState).where(AlertRecipientState.alert_id == "alert-1"))
    assert len(res.scalars().all()) == 0
