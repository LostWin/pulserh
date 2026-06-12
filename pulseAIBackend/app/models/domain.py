import uuid
from datetime import datetime, date
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
    
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")

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

class Document(Base):
    __tablename__ = "documents"
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    size = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    uploaded_by = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(String, primary_key=True, default=generate_uuid)
    user_email = Column(String, nullable=False)
    action = Column(String, nullable=False)
    log_type = Column(String, nullable=False) # auth, security, export, system, ai, access
    ip_address = Column(String, nullable=True)
    critical = Column(Boolean, default=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

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

