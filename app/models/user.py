from enum import Enum
from sqlalchemy import Column, String, Integer, ForeignKey, JSON, TIMESTAMP, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid
import json
from app.config.database import Base

def generate_uuid():
  return str(uuid.uuid4())

class CustomEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, datetime):
      return obj.isoformat()
    elif isinstance(obj, uuid.UUID):
      return str(obj)
    elif isinstance(obj, Enum):
      return obj.name
    return json.JSONEncoder.default(self, obj)
  
class Document(Base):
  __tablename__ = 'documents'

  document_id = Column(UUID(as_uuid=True), primary_key=True)
  organisation_id = Column(UUID(as_uuid=True))
  portfolio_id = Column(UUID(as_uuid=True))
  parentPortfolio_ids = Column(ARRAY(UUID(as_uuid=True)))
  deal_id = Column(UUID(as_uuid=True))
  provider_id = Column(UUID(as_uuid=True))
  parentFolder_ids = Column(ARRAY(UUID(as_uuid=True)))
  folder_id = Column(UUID(as_uuid=True))
  room_id = Column(UUID(as_uuid=True))
  document_name = Column(String)
  created_at = Column(TIMESTAMP)
  updated_at = Column(TIMESTAMP)

  def to_json(self):
    data = {key: value for key, value in vars(self).items() if not key.startswith('_') and not callable(value)}
    return json.loads(json.dumps(data, cls=CustomEncoder))

class Stage(Enum):
  API_REQUEST = 'API_REQUEST'
  DOWNLOAD_WORKER = 'DOWNLOAD_WORKER'
  AI_PIPELINE = 'AI_PIPELINE'
  UPLOAD_WORKER = 'UPLOAD_WORKER'
  MONITOR_WORKER = 'MONITOR_WORKER'

class Status(Enum):
  NOT_STARTED = 'NOT_STARTED'
  IN_PROGRESS = 'IN_PROGRESS'
  COMPLETED = 'COMPLETED'
  TIMEOUT = 'TIMEOUT'
  FAILED = 'FAILED'

class ExtractionType(Enum):
  RENT_ROLL = 'RENT_ROLL'
  LIMITED_PARTNERSHIP_AGREEMENT = 'LIMITED_PARTNERSHIP_AGREEMENT'
  APPRAISAL = 'APPRAISAL'
  CAPITAL_CALL = 'CAPITAL_CALL'

class Extraction(Base):
  __tablename__ = 'extractions'

  extraction_id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
  document_id = Column(UUID(as_uuid=True), ForeignKey('documents.document_id'))
  extraction_type = Column(SQLEnum(ExtractionType))
  extraction_details = Column(JSON)
  status = Column(SQLEnum(Status), default=Status.NOT_STARTED)
  stage = Column(SQLEnum(Stage), default=Stage.API_REQUEST)
  message = Column(Text, nullable=True)
  created_at = Column(TIMESTAMP, default=datetime.now(timezone.utc))
  updated_at = Column(TIMESTAMP, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
  document = relationship("Document", back_populates="extractions")

  def to_json(self):
    data = {key: value for key, value in vars(self).items() if not key.startswith('_') and not callable(value)}
    return json.loads(json.dumps(data, cls=CustomEncoder))

