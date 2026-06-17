import uuid
from datetime import date
from sqlalchemy import Column, String, Float, Integer, ForeignKey, Date, DateTime, Text, Boolean, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class Department(Base):
    __tablename__ = "departments"
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, unique=True, index=True, nullable=False)
    manager_id = Column(String, ForeignKey("employees.id", use_alter=True, name="fk_department_manager"), nullable=True)
    
    # Relationships
    employees = relationship("Employee", back_populates="department", foreign_keys="[Employee.department_id]")

class Job(Base):
    __tablename__ = "jobs"
    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    level = Column(String, nullable=True) # Junior, Mid, Senior, Lead, etc.
    
    employees = relationship("Employee", back_populates="job")

class Employee(Base):
    __tablename__ = "employees"
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, unique=True, index=True, nullable=True) # Linked to Keycloak User ID
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=True)
    hire_date = Column(Date, nullable=False, default=date.today)
    status = Column(String, default="actif") # actif, inactif, suspendu
    
    # Foreign Keys
    department_id = Column(String, ForeignKey("departments.id"), nullable=True)
    job_id = Column(String, ForeignKey("jobs.id"), nullable=True)
    manager_id = Column(String, ForeignKey("employees.id"), nullable=True) # Self-referential
    
    # Relationships
    department = relationship("Department", back_populates="employees", foreign_keys=[department_id])
    job = relationship("Job", back_populates="employees")
    manager = relationship("Employee", remote_side=[id], backref="subordinates")
    contracts = relationship("Contract", back_populates="employee", cascade="all, delete-orphan")
    attendances = relationship("Attendance", back_populates="employee", cascade="all, delete-orphan")
    leaves = relationship("Leave", back_populates="employee", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="assignee")
    skills = relationship("EmployeeSkill", back_populates="employee", cascade="all, delete-orphan")
    training_enrollments = relationship("TrainingEnrollment", back_populates="employee", cascade="all, delete-orphan")
    project_assignments = relationship("ProjectAssignment", back_populates="employee", cascade="all, delete-orphan")
    engagement_snapshots = relationship("EngagementSnapshot", back_populates="employee", cascade="all, delete-orphan")
    benefit_enrollments = relationship("EmployeeBenefit", back_populates="employee", cascade="all, delete-orphan")
    career_paths = relationship("CareerPath", back_populates="employee", cascade="all, delete-orphan")
    mobility_requests = relationship("MobilityRequest", back_populates="employee", cascade="all, delete-orphan")
    promotions = relationship("PromotionHistory", back_populates="employee", cascade="all, delete-orphan")
    prediction_snapshots = relationship("PredictionSnapshot", back_populates="employee", cascade="all, delete-orphan", order_by="PredictionSnapshot.computed_at.desc()")
    performance_reviews = relationship("PerformanceReview", foreign_keys="[PerformanceReview.employee_id]")
    performance_objectives = relationship("PerformanceObjective", foreign_keys="[PerformanceObjective.employee_id]")

class Contract(Base):
    __tablename__ = "contracts"
    id = Column(String, primary_key=True, default=generate_uuid)
    employee_id = Column(String, ForeignKey("employees.id"), nullable=False)
    contract_type = Column(String, nullable=False) # CDI, CDD, Alternance, Stage
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    salary = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)
    
    employee = relationship("Employee", back_populates="contracts")

class Attendance(Base):
    __tablename__ = "attendances"
    id = Column(String, primary_key=True, default=generate_uuid)
    employee_id = Column(String, ForeignKey("employees.id"), nullable=False)
    date = Column(Date, nullable=False)
    check_in = Column(DateTime, nullable=True)
    check_out = Column(DateTime, nullable=True)
    status = Column(String, nullable=False) # Présent, Absent, Retard, Demi-journée
    
    employee = relationship("Employee", back_populates="attendances")

class Leave(Base):
    __tablename__ = "leaves"
    id = Column(String, primary_key=True, default=generate_uuid)
    employee_id = Column(String, ForeignKey("employees.id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    leave_type = Column(String, nullable=False) # Congés Payés, Maladie, Maternité, Autres, Raisons personnelles
    status = Column(String, default="En attente") # En attente, Approuvé, Rejeté
    reason = Column(Text, nullable=True)
    
    employee = relationship("Employee", back_populates="leaves")

class Project(Base):
    __tablename__ = "projects"
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(Date, nullable=True)
    deadline = Column(Date, nullable=True)
    status = Column(String, default="En cours") # En cours, Terminé, En pause, Annulé
    priority = Column(String, nullable=True)
    business_domain = Column(String, nullable=True)
    required_skill_ids = Column(JSON, nullable=True)
    manager_id = Column(String, ForeignKey("employees.id"), nullable=True)
    
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
    assignments = relationship("ProjectAssignment", back_populates="project", cascade="all, delete-orphan")
    manager = relationship("Employee", foreign_keys=[manager_id])

class Skill(Base):
    __tablename__ = "skills"
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False, unique=True, index=True)
    category = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    level_scale = Column(String, nullable=True)
    is_certifiable = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    employee_skills = relationship("EmployeeSkill", back_populates="skill", cascade="all, delete-orphan")
    recommended_trainings = relationship("TrainingCourse", back_populates="target_skill")

class EmployeeSkill(Base):
    __tablename__ = "employee_skills"
    id = Column(String, primary_key=True, default=generate_uuid)
    employee_id = Column(String, ForeignKey("employees.id"), nullable=False, index=True)
    skill_id = Column(String, ForeignKey("skills.id"), nullable=False, index=True)
    proficiency_level = Column(String, nullable=False, default="intermediate")
    years_experience = Column(Float, nullable=True)
    is_primary = Column(Boolean, default=False)
    last_assessed_at = Column(DateTime(timezone=True), nullable=True)
    source = Column(String, nullable=True)
    validated_by = Column(String, nullable=True)
    validated_at = Column(DateTime(timezone=True), nullable=True)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    confidence_score = Column(Float, nullable=True)

    employee = relationship("Employee", back_populates="skills")
    skill = relationship("Skill", back_populates="employee_skills")

class TrainingCourse(Base):
    __tablename__ = "training_courses"
    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String, nullable=False)
    provider = Column(String, nullable=True)
    duration_hours = Column(Float, nullable=True)
    level = Column(String, nullable=True)
    format = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    target_skill_id = Column(String, ForeignKey("skills.id"), nullable=True)
    required_for_job_family = Column(String, nullable=True)
    difficulty = Column(String, nullable=True)
    delivery_mode = Column(String, nullable=True)
    mandatory_for_roles = Column(JSON, nullable=True)

    target_skill = relationship("Skill", back_populates="recommended_trainings")
    enrollments = relationship("TrainingEnrollment", back_populates="training", cascade="all, delete-orphan")

class TrainingEnrollment(Base):
    __tablename__ = "training_enrollments"
    id = Column(String, primary_key=True, default=generate_uuid)
    employee_id = Column(String, ForeignKey("employees.id"), nullable=False, index=True)
    training_id = Column(String, ForeignKey("training_courses.id"), nullable=False, index=True)
    status = Column(String, nullable=False, default="assigned") # assigned, in_progress, completed, overdue
    assigned_at = Column(DateTime(timezone=True), nullable=True)
    due_date = Column(Date, nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    score = Column(Float, nullable=True)
    mandatory = Column(Boolean, default=False)
    assigned_by = Column(String, nullable=True)
    recommendation_reason = Column(Text, nullable=True)

    employee = relationship("Employee", back_populates="training_enrollments")
    training = relationship("TrainingCourse", back_populates="enrollments")

class ProjectAssignment(Base):
    __tablename__ = "project_assignments"
    id = Column(String, primary_key=True, default=generate_uuid)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    employee_id = Column(String, ForeignKey("employees.id"), nullable=False, index=True)
    role_on_project = Column(String, nullable=True)
    allocation_pct = Column(Integer, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)

    project = relationship("Project", back_populates="assignments")
    employee = relationship("Employee", back_populates="project_assignments")

class EngagementSnapshot(Base):
    __tablename__ = "engagement_snapshots"
    id = Column(String, primary_key=True, default=generate_uuid)
    employee_id = Column(String, ForeignKey("employees.id"), nullable=False, index=True)
    score = Column(Integer, nullable=False)
    source = Column(String, nullable=False, default="survey")
    pulse_label = Column(String, nullable=True)
    comment = Column(Text, nullable=True)
    trend = Column(Integer, nullable=True)
    risk_band = Column(String, nullable=True)
    source_signals = Column(JSON, nullable=True)
    captured_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    employee = relationship("Employee", back_populates="engagement_snapshots")


class PredictionSnapshot(Base):
    __tablename__ = "prediction_snapshots"
    id = Column(String, primary_key=True, default=generate_uuid)
    employee_id = Column(String, ForeignKey("employees.id"), nullable=False, index=True)
    prediction_type = Column(String, nullable=False)
    score = Column(Float, nullable=False)
    level = Column(String, nullable=True)
    factors_json = Column(JSON, nullable=True)
    model_version = Column(String, nullable=True)
    computed_at = Column(DateTime(timezone=True), server_default=func.now())

    employee = relationship("Employee", back_populates="prediction_snapshots")


class EngagementEvent(Base):
    __tablename__ = "engagement_events"
    id = Column(String, primary_key=True, default=generate_uuid)
    employee_id = Column(String, ForeignKey("employees.id"), nullable=False, index=True)
    event_type = Column(String, nullable=False)
    label = Column(String, nullable=False)
    intensity = Column(Integer, nullable=False, default=50)
    source = Column(String, nullable=False, default="system")
    payload = Column(JSON, nullable=True)
    occurred_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    employee = relationship("Employee")

class Task(Base):
    __tablename__ = "tasks"
    id = Column(String, primary_key=True, default=generate_uuid)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    assignee_id = Column(String, ForeignKey("employees.id"), nullable=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, default="À faire") # À faire, En cours, En revue, Terminé
    due_date = Column(Date, nullable=True)
    evaluation_score = Column(Float, nullable=True) # Score de performance /10 ou /100 à la complétion
    
    project = relationship("Project", back_populates="tasks")
    assignee = relationship("Employee", back_populates="tasks")

from sqlalchemy import JSON
class ImportHistory(Base):
    __tablename__ = "import_history"
    id = Column(String, primary_key=True, default=generate_uuid)
    filename = Column(String, nullable=False)
    entity_type = Column(String, nullable=False)
    author_name = Column(String, nullable=True)
    processed_lines = Column(Integer, default=0)
    created_lines = Column(Integer, default=0)
    updated_lines = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    status = Column(String, nullable=False) # success, warning, error
    full_report = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(String, nullable=False)

class DocumentType(Base):
    __tablename__ = "document_types"
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    code = Column(String, unique=True, index=True, nullable=False)
    allowed_roles = Column(JSON, nullable=False, default=list)
    responsible_role = Column(String, nullable=True)
    required_variables = Column(JSON, nullable=False, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    templates = relationship("DocumentTemplate", back_populates="document_type", cascade="all, delete-orphan")

class BaseTemplate(Base):
    __tablename__ = "base_templates"
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    html_content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    templates = relationship("DocumentTemplate", back_populates="base_template")

class DocumentTemplate(Base):
    __tablename__ = "document_templates"
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    document_type_id = Column(String, ForeignKey("document_types.id"), nullable=False)
    base_template_id = Column(String, ForeignKey("base_templates.id"), nullable=False)
    html_content = Column(Text, nullable=False)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    document_type = relationship("DocumentType", back_populates="templates")
    base_template = relationship("BaseTemplate", back_populates="templates")

class Document(Base):
    __tablename__ = "documents"
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    size = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    uploaded_by = Column(String, nullable=True)
    allowed_roles = Column(JSON, nullable=False, default=lambda: ["hr", "admin"])
    
    # Nouvelles colonnes pour le workflow IA
    status = Column(String, nullable=False, default="validated") # pending, validated, rejected
    employee_id = Column(String, ForeignKey("employees.id"), nullable=True)
    document_type_id = Column(String, ForeignKey("document_types.id"), nullable=True)

    rag_enabled = Column(Boolean, default=False)
    rag_status = Column(String, nullable=False, default="disabled")
    rag_last_synced_at = Column(DateTime(timezone=True), nullable=True)
    rag_error = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    access_events = relationship("DocumentAccessEvent", back_populates="document", cascade="all, delete-orphan", order_by="DocumentAccessEvent.created_at.desc()")
    employee = relationship("Employee", foreign_keys=[employee_id])
    document_type = relationship("DocumentType")

class DocumentAccessEvent(Base):
    __tablename__ = "document_access_events"
    id = Column(String, primary_key=True, default=generate_uuid)
    document_id = Column(String, ForeignKey("documents.id"), nullable=False, index=True)
    user_email = Column(String, nullable=False)
    action = Column(String, nullable=False)  # view, download, permissions_update, rag_sync, rag_disable
    roles = Column(JSON, nullable=False, default=list)
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    document = relationship("Document", back_populates="access_events")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(String, primary_key=True, default=generate_uuid)
    user_email = Column(String, nullable=False)
    action = Column(String, nullable=False)
    log_type = Column(String, nullable=False) # auth, security, export, system, ai, access
    ip_address = Column(String, nullable=True)
    critical = Column(Boolean, default=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())


class DataAccessPolicy(Base):
    __tablename__ = "data_access_policies"
    id = Column(String, primary_key=True, default=generate_uuid)
    resource = Column(String, nullable=False, index=True)
    scope = Column(String, nullable=False, index=True)
    field_key = Column(String, nullable=False, index=True)
    role = Column(String, nullable=False, index=True)
    visibility = Column(String, nullable=False, default="visible")  # visible, masked, hidden, readonly
    mask_type = Column(String, nullable=True)  # phone, email, full
    conditions_json = Column(JSON, nullable=True)
    description = Column(Text, nullable=True)
    updated_by = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Conversation(Base):
    """Historique des conversations chat IA"""
    __tablename__ = "conversations"
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, nullable=False, index=True)
    title = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    messages = relationship("ChatMessage", back_populates="conversation", cascade="all, delete-orphan", order_by="ChatMessage.created_at")

class ChatMessage(Base):
    """Messages individuels dans une conversation"""
    __tablename__ = "chat_messages"
    id = Column(String, primary_key=True, default=generate_uuid)
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False, index=True)
    role = Column(String, nullable=False)  # "user", "assistant", "system", "tool"
    content = Column(Text, nullable=True)
    tool_calls = Column(JSON, nullable=True)    # Appels d'outils effectués par l'IA
    tool_results = Column(JSON, nullable=True)  # Résultats des outils
    sources = Column(JSON, nullable=True)       # Sources RAG utilisées
    tokens_used = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    conversation = relationship("Conversation", back_populates="messages")

class Guardrail(Base):
    """Règles de filtrage IA configurables depuis l'interface admin"""
    __tablename__ = "guardrails"
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    pattern = Column(String, nullable=False)        # Regex ou mot-clé
    action = Column(String, nullable=False)          # "block", "warn", "redact"
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=0)
    triggered_count = Column(Integer, default=0)
    created_by = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AIConfiguration(Base):
    """Configuration IA persistante (singleton en DB)"""
    __tablename__ = "ai_configuration"
    id = Column(String, primary_key=True, default=generate_uuid)
    provider = Column(String, default="openrouter")   # "openrouter" | "ollama"
    model_name = Column(String, default="mistralai/mistral-7b-instruct")
    temperature = Column(Float, default=0.7)
    max_tokens = Column(Integer, default=2048)
    system_prompt = Column(Text, default="Tu es Pulse AI, un assistant RH intelligent. Tu aides les collaborateurs avec leurs questions sur les congés, la paie, les formations et les démarches administratives. Tu es professionnel, empathique et précis. Tu ne divulgues jamais d'informations confidentielles au-delà du rôle de l'utilisateur.")
    guardrails_enabled = Column(Boolean, default=True)
    updated_by = Column(String, nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Workflow(Base):
    __tablename__ = "workflows"
    id = Column(String, primary_key=True, default=generate_uuid)
    type = Column(String, nullable=False) # onboarding, offboarding
    employee_id = Column(String, ForeignKey("employees.id"), nullable=False)
    status = Column(String, default="generating") # generating, draft, running, completed, failed
    progress_percent = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    employee = relationship("Employee", backref="workflows")
    steps = relationship("WorkflowStep", back_populates="workflow", cascade="all, delete-orphan", order_by="WorkflowStep.sequence")

class WorkflowStep(Base):
    __tablename__ = "workflow_steps"
    id = Column(String, primary_key=True, default=generate_uuid)
    workflow_id = Column(String, ForeignKey("workflows.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    assigned_to = Column(String, nullable=True) # employee_id, role, or team
    step_type = Column(String, default="automated") # automated, manual, external_ticket
    status = Column(String, default="pending") # pending, running, done, failed
    due_date = Column(DateTime(timezone=True), nullable=True)
    executed_at = Column(DateTime(timezone=True), nullable=True)
    urgency = Column(String, default="medium") # low, medium, high
    priority = Column(Integer, default=3) # 1 highest
    sequence = Column(Integer, default=0) # For ordering
    rationale = Column(Text, nullable=True) # AI explanation
    external_ticket_id = Column(String, nullable=True)

    workflow = relationship("Workflow", back_populates="steps")

class NotificationConfig(Base):
    __tablename__ = "notification_configs"
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, nullable=False, index=True) # Could link to employees or keycloak user
    email_enabled = Column(Boolean, default=True)
    in_app_enabled = Column(Boolean, default=True)
    slack_enabled = Column(Boolean, default=False)


class UserPreference(Base):
    __tablename__ = "user_preferences"
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, nullable=False, unique=True, index=True)
    avatar_data_url = Column(Text, nullable=True)
    theme = Column(String, nullable=False, default="dark")
    locale = Column(String, nullable=False, default="fr")
    timezone = Column(String, nullable=False, default="Africa/Lome")
    digest_frequency = Column(String, nullable=False, default="daily")
    profile_title = Column(String, nullable=True)
    birth_date_label = Column(String, nullable=True)
    address_label = Column(Text, nullable=True)
    work_location_label = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Interview(Base):
    __tablename__ = "interviews"
    id = Column(String, primary_key=True, default=generate_uuid)
    employee_id = Column(String, ForeignKey("employees.id"), nullable=False, index=True)
    manager_id = Column(String, ForeignKey("employees.id"), nullable=False, index=True)
    title = Column(String, nullable=False, default="Entretien individuel")
    interview_type = Column(String, nullable=False, default="one_on_one")
    scheduled_at = Column(DateTime(timezone=True), nullable=False)
    status = Column(String, nullable=False, default="Planifié")
    location = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    outcome = Column(String, nullable=True)
    summary = Column(Text, nullable=True)
    next_actions = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    employee = relationship("Employee", foreign_keys=[employee_id])
    manager = relationship("Employee", foreign_keys=[manager_id])


class GeneratedReport(Base):
    __tablename__ = "generated_reports"
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    period = Column(String, nullable=False)
    department_filter = Column(String, nullable=True)
    format = Column(String, nullable=False, default="PDF")
    file_path = Column(String, nullable=False)
    size = Column(String, nullable=True)
    status = Column(String, nullable=False, default="ready")
    created_by = Column(String, nullable=False)
    meta_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class PerformanceReview(Base):
    __tablename__ = "performance_reviews"
    id = Column(String, primary_key=True, default=generate_uuid)
    employee_id = Column(String, ForeignKey("employees.id"), nullable=False, index=True)
    reviewer_id = Column(String, ForeignKey("employees.id"), nullable=True, index=True)
    review_type = Column(String, nullable=False, default="quarterly")
    period_label = Column(String, nullable=False)
    score = Column(Float, nullable=False)
    summary = Column(Text, nullable=True)
    strengths = Column(JSON, nullable=True)
    improvement_areas = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    employee = relationship("Employee", foreign_keys=[employee_id])
    reviewer = relationship("Employee", foreign_keys=[reviewer_id])


class PerformanceObjective(Base):
    __tablename__ = "performance_objectives"
    id = Column(String, primary_key=True, default=generate_uuid)
    employee_id = Column(String, ForeignKey("employees.id"), nullable=False, index=True)
    owner_id = Column(String, ForeignKey("employees.id"), nullable=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, nullable=False, default="planned")
    progress_pct = Column(Integer, nullable=False, default=0)
    target_date = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    employee = relationship("Employee", foreign_keys=[employee_id])
    owner = relationship("Employee", foreign_keys=[owner_id])


class BenefitPlan(Base):
    __tablename__ = "benefit_plans"
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    provider = Column(String, nullable=True)
    category = Column(String, nullable=False, default="general")
    coverage_summary = Column(Text, nullable=True)
    enrollment_month = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    employee_benefits = relationship("EmployeeBenefit", back_populates="benefit_plan", cascade="all, delete-orphan")


class EmployeeBenefit(Base):
    __tablename__ = "employee_benefits"
    id = Column(String, primary_key=True, default=generate_uuid)
    employee_id = Column(String, ForeignKey("employees.id"), nullable=False, index=True)
    benefit_plan_id = Column(String, ForeignKey("benefit_plans.id"), nullable=False, index=True)
    status = Column(String, nullable=False, default="active")
    effective_date = Column(Date, nullable=True)
    renewal_date = Column(Date, nullable=True)
    tier_label = Column(String, nullable=True)
    employer_contribution = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    employee = relationship("Employee", back_populates="benefit_enrollments")
    benefit_plan = relationship("BenefitPlan", back_populates="employee_benefits")


class CareerPath(Base):
    __tablename__ = "career_paths"
    id = Column(String, primary_key=True, default=generate_uuid)
    employee_id = Column(String, ForeignKey("employees.id"), nullable=False, index=True)
    target_job_id = Column(String, ForeignKey("jobs.id"), nullable=True, index=True)
    target_title = Column(String, nullable=False)
    readiness_level = Column(String, nullable=False, default="emerging")
    next_step = Column(Text, nullable=True)
    mentor_name = Column(String, nullable=True)
    last_reviewed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    employee = relationship("Employee", back_populates="career_paths")
    target_job = relationship("Job")


class MobilityRequest(Base):
    __tablename__ = "mobility_requests"
    id = Column(String, primary_key=True, default=generate_uuid)
    employee_id = Column(String, ForeignKey("employees.id"), nullable=False, index=True)
    target_department_id = Column(String, ForeignKey("departments.id"), nullable=True, index=True)
    target_job_id = Column(String, ForeignKey("jobs.id"), nullable=True, index=True)
    request_type = Column(String, nullable=False, default="internal_move")
    status = Column(String, nullable=False, default="draft")
    rationale = Column(Text, nullable=True)
    requested_at = Column(DateTime(timezone=True), server_default=func.now())
    reviewed_at = Column(DateTime(timezone=True), nullable=True)

    employee = relationship("Employee", back_populates="mobility_requests")
    target_department = relationship("Department")
    target_job = relationship("Job")


class PromotionHistory(Base):
    __tablename__ = "promotion_history"
    id = Column(String, primary_key=True, default=generate_uuid)
    employee_id = Column(String, ForeignKey("employees.id"), nullable=False, index=True)
    previous_job_title = Column(String, nullable=True)
    new_job_title = Column(String, nullable=False)
    effective_date = Column(Date, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    employee = relationship("Employee", back_populates="promotions")


class Alert(Base):
    __tablename__ = "alerts"
    id = Column(String, primary_key=True, default=generate_uuid)
    fingerprint = Column(String, nullable=False, unique=True, index=True)
    type = Column(String, nullable=False)
    severity = Column(String, nullable=False, default="medium")
    title = Column(String, nullable=False)
    message = Column(Text, nullable=True)
    status = Column(String, nullable=False, default="open")
    source = Column(String, nullable=False, default="pulse_ai")
    employee_id = Column(String, ForeignKey("employees.id"), nullable=True, index=True)
    workflow_id = Column(String, ForeignKey("workflows.id"), nullable=True, index=True)
    target_user_id = Column(String, nullable=True, index=True)
    target_roles = Column(JSON, nullable=True)
    link = Column(String, nullable=True)
    payload = Column(JSON, nullable=True)
    action_plan = Column(Text, nullable=True)
    resolved_by = Column(String, nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    employee = relationship("Employee")
    workflow = relationship("Workflow")
    recipients = relationship("AlertRecipientState", back_populates="alert", cascade="all, delete-orphan")


class AlertRecipientState(Base):
    __tablename__ = "alert_recipient_states"
    id = Column(String, primary_key=True, default=generate_uuid)
    alert_id = Column(String, ForeignKey("alerts.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)
    status = Column(String, nullable=False, default="unread")  # unread, read, archived
    read_at = Column(DateTime(timezone=True), nullable=True)
    archived_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    alert = relationship("Alert", back_populates="recipients")

class AIObservabilityEvent(Base):
    """Logs techniques des interactions IA (Tool calling, fallbacks, erreurs)"""
    __tablename__ = "ai_observability_events"
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, nullable=True, index=True)
    event_type = Column(String, nullable=False) # e.g. "prediction", "chat", "tool_call", "rag_search"
    status = Column(String, nullable=False)     # "success", "error", "fallback"
    duration_ms = Column(Integer, nullable=True)
    tokens_used = Column(Integer, nullable=True, default=0)
    details_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class TemplateAsset(Base):
    __tablename__ = "template_assets"
    id = Column(String, primary_key=True, default=generate_uuid)
    key = Column(String, unique=True, nullable=False, index=True)
    value = Column(Text, nullable=False)
    asset_type = Column(String, nullable=False, default="text") # "text", "image_url", "image_base64"
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class MLModuleConfig(Base):
    """Configuration persistante par module ML/heuristique (une ligne par module)."""
    __tablename__ = "ml_module_configs"

    id = Column(String, primary_key=True, default=generate_uuid)
    module_id = Column(String, nullable=False, unique=True, index=True)  # ex: "CHURN_RISK"
    module_name = Column(String, nullable=False)
    is_enabled = Column(Boolean, default=True)
    mode = Column(String, default="heuristic")              # "heuristic" | "ml"

    # Config partagée (communes aux deux modes)
    alert_threshold = Column(Float, default=0.70)           # Seuil d'alerte (0.0–1.0)
    strict_mode = Column(Boolean, default=False)            # Validation humaine obligatoire

    # Config Heuristique (JSON)
    heuristic_params = Column(JSON, default=dict)

    # Config ML (JSON)
    ml_params = Column(JSON, default=dict)
    model_version = Column(String, nullable=True)           # ex: "xgboost_churn_v1.2"
    last_trained_at = Column(DateTime(timezone=True), nullable=True)
    training_status = Column(String, default="untrained")   # "untrained"|"training"|"ready"|"error"
    training_error = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

