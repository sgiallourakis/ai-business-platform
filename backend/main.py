#main.py
from fastapi import FastAPI, File, UploadFile, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import pandas as pd
from io import StringIO, BytesIO
import json
from datetime import datetime

from database import get_db
from models import DataUpload, Analysis

app = FastAPI(title="AI Business Platform", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Business Platform API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/uploads")
def get_uploads(db: Session = Depends(get_db)):
    """
    Get all uploaded files ordered by newest first
    """
    try:
        uploads = db.query(DataUpload).order_by(DataUpload.upload_time.desc()).all()
        return [
            {
                "id": upload.id,
                "filename": upload.filename,
                "file_type": upload.file_type,
                "upload_time": upload.upload_time,
                "status": upload.status
            }
            for upload in uploads
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/analysis/{upload_id}")
def get_analysis(upload_id: int, db: Session = Depends(get_db)):
    """
    Get analysis results for a specific upload
    """
    try:
        analysis = db.query(Analysis).filter(Analysis.data_upload_id == upload_id).first()
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        return {
            "id": analysis.id,
            "analysis_type": analysis.analysis_type,
            "result": json.loads(analysis.result),
            "confidence": analysis.confidence,
            "created_at": analysis.created_at
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db) 
): 
    """
    Upload, validate, and analyze a CSV/Excel file
    """
    upload_record = None
    
    try:
        # Validate file type
        allowed_types = ["text/csv", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail="Only CSV and Excel files are supported"
            )

        # Determine file type
        file_type = "csv" if file.content_type == "text/csv" else "xlsx"

        # Save upload record to database
        upload_record = DataUpload(
            filename=file.filename,
            file_type=file_type,
            status="processing"
        )
        db.add(upload_record)
        db.commit()
        db.refresh(upload_record)

        # Read file content
        content = await file.read()
        
        # Process the file with pandas
        if file_type == "csv":
            df = pd.read_csv(StringIO(content.decode('utf-8')))
        else:
            df = pd.read_excel(BytesIO(content))
        
        # Generate data analysis
        analysis_result = {
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": df.columns.tolist(),
            "data_types": df.dtypes.astype(str).to_dict(),
            "sample_data": df.head(5).fillna("null").to_dict('records'),  # Replace NaN with "null"
            "missing_values": df.isnull().sum().to_dict(),
            "numeric_summary": df.select_dtypes(include=['number']).describe().fillna(0).to_dict() if not df.select_dtypes(include=['number']).empty else {}
        
        }
                
        # Save analysis to database
        analysis_record = Analysis(
            data_upload_id=upload_record.id,
            analysis_type="data_summary",
            result=json.dumps(analysis_result),
            confidence=1.0
        )
        db.add(analysis_record)
        
        # Update upload status to analyzed
        upload_record.status = "analyzed"
        db.commit()
        
        return {
            "upload_id": upload_record.id,
            "filename": upload_record.filename,
            "message": "File uploaded successfully",
            "status": "analyzed",
            "analysis": analysis_result
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Handle any other errors
        if upload_record:
            upload_record.status = "error"
            db.commit()
        
        raise HTTPException(
            status_code=422, 
            detail=f"Failed to process file: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)