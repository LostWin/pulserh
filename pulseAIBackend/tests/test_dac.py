import pytest
from app.services.field_access_service import mask_value, apply_field_access
from app.models.domain import DataAccessPolicy

def test_mask_value_email():
    assert mask_value("john.doe@example.com", "email") == "jo***@example.com"
    assert mask_value("ab@foo.com", "email") == "a***@foo.com"
    assert mask_value("invalid-email", "email") == "••••"
    assert mask_value(None, "email") is None

def test_mask_value_phone():
    assert mask_value("+33612345678", "phone") == "*** *** 78"
    assert mask_value("0612345678", "phone") == "*** *** 78"
    assert mask_value("123", "phone") == "*** *** 23"
    assert mask_value(None, "phone") is None

def test_mask_value_full():
    assert mask_value("Secret Data", "full") == "••••"
    assert mask_value("12345", "full") == "••••"
    assert mask_value(None, "full") is None

@pytest.mark.asyncio
async def test_apply_field_access_collaborator():
    # Simulate DB rows for DataAccessPolicy
    policies = [
        DataAccessPolicy(resource="employee", scope="detail", field_key="salary", role="collaborator", visibility="hidden"),
        DataAccessPolicy(resource="employee", scope="detail", field_key="phone", role="collaborator", visibility="masked", mask_type="phone"),
        DataAccessPolicy(resource="employee", scope="detail", field_key="performance_score", role="collaborator", visibility="visible"),
    ]
    
    # Simulate raw db dict
    raw_data = {
        "first_name": "Alice",
        "salary": 50000,
        "phone": "0612345678",
        "performance_score": 85,
    }

    # Simulate apply_field_access behavior using dummy get_effective_policies
    class MockDB:
        async def execute(self, query):
            class MockResult:
                def scalars(self):
                    class MockScalars:
                        def all(self):
                            return policies
                    return MockScalars()
            return MockResult()
            
    db = MockDB()
    user_roles = ["collaborator"]
    employee_id = "target_emp_id"
    user_id = "user_id"
    user_department = "IT"

    # Context build
    context = {
        "user_id": user_id,
        "target_employee_id": employee_id,
        "user_roles": user_roles,
        "user_department": user_department,
    }
    
    result, visibility = await apply_field_access(db, resource="employee", scope="detail", payload=raw_data, role="collaborator", context=context)
    
    # The salary should be None
    assert result["salary"] is None
    # The phone should be masked
    assert result["phone"] == "*** *** 78"
    # The performance_score should be untouched
    assert result["performance_score"] == 85
    # The first_name has no specific policy so it falls back to default visible
    assert result["first_name"] == "Alice"
    assert visibility["salary"] == "hidden"
    assert visibility["phone"] == "masked"

@pytest.mark.asyncio
async def test_apply_field_access_hr_override():
    # HR should have higher priority, if HR can see salary but collaborator can't
    policies = [
        DataAccessPolicy(resource="employee", scope="detail", field_key="salary", role="collaborator", visibility="hidden"),
        DataAccessPolicy(resource="employee", scope="detail", field_key="salary", role="hr", visibility="visible"),
    ]
    
    raw_data = {"salary": 50000}
    
    class MockDB:
        async def execute(self, query):
            class MockResult:
                def scalars(self):
                    class MockScalars:
                        def all(self):
                            return policies
                    return MockScalars()
            return MockResult()
            
    db = MockDB()
    user_roles = ["collaborator", "hr"]  # User is both
    context = {
        "user_id": "1",
        "target_employee_id": "2",
        "user_roles": user_roles,
        "user_department": "HR",
    }
    
    # Normally the route handles multi roles and picks highest, but apply_field_access tests one role
    # So let's test for role="hr"
    result, visibility = await apply_field_access(db, resource="employee", scope="detail", payload=raw_data, role="hr", context=context)
    
    assert "salary" in result
    assert result["salary"] == 50000
    assert visibility["salary"] == "visible"
