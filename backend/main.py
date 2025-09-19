#main.py
from fastapi import FastAPI, File, UploadFile, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
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

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db) 
): 
    """
    Upload and validate a CSV/Excel file for analysis
    """
    try:
        # Validate file type
        allowed_types = ["text/csv", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Only CSV and Excel files are allowed."
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

        return {
            "upload_id": upload_record.id,
            "filename": upload_record.filename,
            "message": "File uploaded successfully and is being processed.",
            "status": "processing"
        }

    except HTTPException:
        # Re-raise HTTP exceptions (like file type validation)
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)