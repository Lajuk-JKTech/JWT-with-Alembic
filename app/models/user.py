from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Integer, String, func, JSON, Index, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.config.database import Base

class VM_Users(Base):
    __tablename__ = 'vm_users'

    # Columns
    eventid = Column(String, nullable=True)
    aggregateid = Column(UUID, primary_key=True, nullable=False)
    aggregatetype = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    email = Column(String, nullable=False)
    title = Column(String, nullable=True)
    company = Column(String, nullable=True)
    image = Column(String, nullable=True)
    accepted_tc_version = Column(String, nullable=True, default='-1')

    # Enums for status and assignee_type
    status = Column(Enum('Not Invited', 'Active', 'Inactive', name='user_status_enum'), nullable=True, default='Not Invited')
    invite_accepted = Column(Boolean, default=False)
    assignee_type = Column(Enum('USER', 'ADMIN', name='user_assignee_type_enum'), nullable=True, default='USER')
    
    active_platform_user = Column(Boolean, default=True, nullable=False)
    profile = Column(JSONB, nullable=True)

    created_by = Column(UUID, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    updated_by = Column(UUID, nullable=True)
    
    version = Column(Integer, nullable=False, default=0)

    # Indexes
    __table_args__ = (
        Index('vm_user_name_idx', func.lower(first_name), func.lower(last_name)),  # Index on lower(first_name), lower(last_name)
        Index('vm_user_aggregate_idx', 'aggregateid'),  # Index on aggregateid
        Index('user_vm_email_udx', func.lower(email), unique=True)  # Unique index on lower(email)
    )

