# models.py - Database Models for AI Business Platform
"""
This file defines the database schema using SQLAlchemy ORM.
Each class represents a table in the PostgreSQL database.
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Float
from sqlalchemy.sql import func
from database import Base  # Import the Base class for creating models


class DataUpload(Base):
    """
    Represents files uploaded by users for analysis.
    
    This table tracks all data files (CSV, Excel, etc.) that users upload
    to the platform for AI analysis.
    """
    __tablename__ = "data_uploads"  # Name of the table in the database
    
    # Primary key - unique identifier for each upload
    id = Column(Integer, primary_key=True, index=True)
    
    # Original filename when uploaded (e.g., "sales_data.csv")
    filename = Column(String, index=True)  # Index for faster searching
    
    # Type of file uploaded (e.g., "csv", "xlsx", "json")
    file_type = Column(String)
    
    # When the file was uploaded (automatically set by database)
    upload_time = Column(DateTime, server_default=func.now())
    
    # Current status of the upload (e.g., "uploaded", "processing", "analyzed", "error")
    status = Column(String, default="uploaded")


class Analysis(Base):
    """
    Stores AI analysis results for uploaded data.
    
    Each row represents one AI analysis performed on uploaded data.
    Multiple analyses can be performed on the same data upload.
    """
    __tablename__ = "analyses"  # Name of the table in the database
    
    # Primary key - unique identifier for each analysis
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key linking to the DataUpload that was analyzed
    # This connects analyses to their source data
    data_upload_id = Column(Integer)  # References DataUpload.id
    
    # Type of AI analysis performed
    # Examples: 'sentiment', 'forecast', 'classification', 'clustering'
    analysis_type = Column(String)
    
    # AI analysis results stored as JSON string
    # Example: '{"sentiment": "positive", "confidence": 0.85, "topics": ["product", "price"]}'
    result = Column(Text)  # Text type for large JSON data
    
    # Confidence score of the AI prediction (0.0 to 1.0)
    # Higher values mean the AI is more confident in its prediction
    confidence = Column(Float)
    
    # When this analysis was performed (automatically set by database)
    created_at = Column(DateTime, server_default=func.now())


# Future model ideas for expansion:
# 
# class User(Base):
#     """User accounts for multi-tenant platform"""
#     __tablename__ = "users"
#     id = Column(Integer, primary_key=True)
#     email = Column(String, unique=True, index=True)
#     hashed_password = Column(String)
#     created_at = Column(DateTime, server_default=func.now())
#
# class Model(Base):
#     """Custom trained ML models"""
#     __tablename__ = "models"
#     id = Column(Integer, primary_key=True)
#     name = Column(String)
#     model_type = Column(String)  # 'custom_sentiment', 'forecasting', etc.
#     model_path = Column(String)  # File path to saved model
#     accuracy = Column(Float)
#     created_at = Column(DateTime, server_default=func.now())
#
# class Prediction(Base):
#     """Real-time predictions using trained models"""
#     __tablename__ = "predictions"
#     id = Column(Integer, primary_key=True)
#     model_id = Column(Integer)  # References Model.id
#     input_data = Column(Text)  # JSON of input data
#     prediction = Column(Text)  # JSON of prediction results
#     created_at = Column(DateTime, server_default=func.now())