import asyncio
from app.database import AsyncSessionLocal
from app.services.import_service import process_csv_import
from app.schemas.import_schemas import DepartmentImport
from app.models.domain import Department

async def run():
    async with AsyncSessionLocal() as db:
        with open("data_imports/01_departments.csv", "rb") as f:
            class MockFile:
                filename = "01_departments.csv"
                async def read(self):
                    return f.read()
            
            try:
                report = await process_csv_import(MockFile(), db, DepartmentImport, Department, "test_user", "departments")
                print("REPORT:", report)
            except Exception as e:
                print("EXCEPTION:", e)

asyncio.run(run())
