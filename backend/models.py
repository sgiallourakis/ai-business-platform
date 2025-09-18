from sqlalchemy import Column, Integer, String, DateTime, Text, Float
from sqlalchemy.sql import func
from database import Base

class DataUpload(Base):
    __tablename__ = "data_uploads"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    file_type = Column(String)
    upload_time = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, default="processing")
                    
class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    data_upload_id = Column(Integer)
    analysis_type = Column(String)
    result = Column(Text) # JSON or text result
    confidence = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
