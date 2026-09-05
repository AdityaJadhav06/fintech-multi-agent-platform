import uuid
from datetime import datetime
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    JSON,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


def generate_uuid() -> str:
    return str(uuid.uuid4())


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    subscription_tier = Column(String(50), default="enterprise")
    created_at = Column(DateTime, default=datetime.utcnow)

    users = relationship("User", back_populates="organization")
    cases = relationship("Case", back_populates="organization")


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    org_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    auth0_sub = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), nullable=False)
    role = Column(String(50), default="analyst")
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="users")


class RolePermission(Base):
    __tablename__ = "roles_permissions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    role_name = Column(String(50), nullable=False)
    resource = Column(String(100), nullable=False)
    can_read = Column(Boolean, default=True)
    can_write = Column(Boolean, default=False)
    can_approve = Column(Boolean, default=False)


class Case(Base):
    __tablename__ = "cases"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    org_id = Column(String(36), ForeignKey("organizations.id"), nullable=False, index=True)
    created_by = Column(String(36), nullable=True)
    title = Column(String(255), nullable=False)
    master_question = Column(Text, nullable=False)
    business_context = Column(Text, default="")
    constraints_json = Column(JSON, default=dict)
    status = Column(String(50), default="PENDING")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    organization = relationship("Organization", back_populates="cases")
    documents = relationship("Document", back_populates="case", cascade="all, delete-orphan")
    agent_runs = relationship("AgentRun", back_populates="case", cascade="all, delete-orphan")
    risks = relationship("Risk", back_populates="case", cascade="all, delete-orphan")
    approvals = relationship("Approval", back_populates="case", cascade="all, delete-orphan")


class Job(Base):
    __tablename__ = "jobs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    case_id = Column(String(36), ForeignKey("cases.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    case_id = Column(String(36), ForeignKey("cases.id"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), default="txt")
    file_size = Column(Integer, default=0)
    storage_path = Column(String(500), nullable=True)
    uploaded_by = Column(String(36), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    case = relationship("Case", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("documents.id"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    content_text = Column(Text, nullable=False)
    metadata_json = Column(JSON, default=dict)

    document = relationship("Document", back_populates="chunks")
    embedding = relationship("Embedding", back_populates="chunk", uselist=False, cascade="all, delete-orphan")


class Embedding(Base):
    __tablename__ = "embeddings"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    chunk_id = Column(String(36), ForeignKey("document_chunks.id"), nullable=False, unique=True)
    vector_json = Column(JSON, nullable=False)  # Float array stored as JSON for universal DB compatibility
    model_name = Column(String(100), default="nomic-embed-text")
    dimensions = Column(Integer, default=384)

    chunk = relationship("DocumentChunk", back_populates="embedding")


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    case_id = Column(String(36), ForeignKey("cases.id"), nullable=False, index=True)
    agent_name = Column(String(50), nullable=False)
    status = Column(String(50), default="PENDING")
    summary = Column(Text, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)

    case = relationship("Case", back_populates="agent_runs")
    findings = relationship("AgentFinding", back_populates="run", cascade="all, delete-orphan")


class AgentFinding(Base):
    __tablename__ = "agent_findings"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    run_id = Column(String(36), ForeignKey("agent_runs.id"), nullable=False)
    case_id = Column(String(36), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(100), default="General")
    severity = Column(String(50), default="MEDIUM")
    structured_json = Column(JSON, default=dict)
    human_review_required = Column(Boolean, default=False)

    run = relationship("AgentRun", back_populates="findings")


class Risk(Base):
    __tablename__ = "risks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    case_id = Column(String(36), ForeignKey("cases.id"), nullable=False, index=True)
    source_agent = Column(String(50), nullable=False)
    risk_code = Column(String(50), nullable=True)
    description = Column(Text, nullable=False)
    probability = Column(String(50), default="UNKNOWN")
    impact = Column(String(50), default="UNKNOWN")
    severity_score = Column(Integer, default=4)
    mitigation = Column(Text, nullable=False)
    owner = Column(String(100), nullable=True)
    status = Column(String(50), default="OPEN")
    created_at = Column(DateTime, default=datetime.utcnow)

    case = relationship("Case", back_populates="risks")


class Approval(Base):
    __tablename__ = "approvals"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    case_id = Column(String(36), ForeignKey("cases.id"), nullable=False, index=True)
    run_id = Column(String(36), nullable=True)
    category = Column(String(100), nullable=False)
    reason = Column(Text, nullable=False)
    decision = Column(String(50), default="PENDING")  # PENDING, APPROVED, REJECTED
    reviewer_id = Column(String(36), nullable=True)
    comments = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    reviewed_at = Column(DateTime, nullable=True)

    case = relationship("Case", back_populates="approvals")


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    org_id = Column(String(36), nullable=False, index=True)
    user_id = Column(String(36), nullable=True)
    case_id = Column(String(36), nullable=True, index=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(String(100), nullable=True)
    payload_hash = Column(String(64), nullable=True)
    details_json = Column(JSON, default=dict)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
