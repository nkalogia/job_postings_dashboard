from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException, Request, Response
from fastapi.responses import StreamingResponse
from sqlalchemy import ext
from sqlalchemy.orm import Session
import io
from csv import DictWriter
import uvicorn
from datetime import timezone

import crud, models, schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/jobs", response_model=schemas.Job)
def create_job(job: schemas.Job, request: Request, db: Session = Depends(get_db)):
    """Create a job resource and save it to the database if it does not exist."""
    db_job = crud.get_job(db, job_id=job.id)
    if db_job:
        raise HTTPException(status_code=303, detail="Job already exists", headers={'Location': request.url.path+'/'+str(db_job.id)})
    return crud.create_or_update_job(db=db, job=job)


@app.put("/jobs/{job_id}", response_model=schemas.Job)
def update_job(job: schemas.Job, db: Session = Depends(get_db)):
    """Update the job resource."""
    return crud.create_or_update_job(db=db, job=job)


def get_jobs_csv(jobs: List[models.Job]):
    """Unwind the jobs collection and generate each line."""
    f = io.StringIO()
    fieldnames = ['id', 'title', 'technologies',
                  'employer_name', 'employer_size',
                  'employer_industries', 'employer_company_type',
                  'experience', 'roles', 'job_types',
                  'joel_test', 'skills', 'created',
                  'location_longitude', 'location_latitude', 'location_country_code',
                  'salary_minimum', 'salary_maximum',
                  'visa', 'equity', 'relocation',
                  'benefits', 'remote']
    dw = DictWriter(f, fieldnames, extrasaction='ignore')
    dw.writeheader()
    yield f.getvalue()
    for job in jobs:
        for row in crud.unwind(crud.flatten(schemas.Job.from_orm(job).dict())):
            f = io.StringIO()
            dw = DictWriter(f, fieldnames, extrasaction='ignore')
            dw.writerow(row)
            yield f.getvalue()


@app.get("/jobs", response_model=List[schemas.Job])
def read_jobs(offset: int = 0, limit: Optional[int] = None, format: str = 'json', db: Session = Depends(get_db)):
    """Get the jobs collection."""
    if format == 'csv':
        jobs = crud.get_jobs(db, offset=0)
        return StreamingResponse(
            crud.get_jobs_csv(jobs), 
            media_type='text/csv',
            headers={'Content-Disposition':"attachment; filename=jobs.csv"})
    else:
        jobs = crud.get_jobs(db=db, offset=offset, limit=limit)
        return jobs


@app.get("/jobs/{job_id}", response_model=schemas.Job)
def read_job(job_id: int, db: Session = Depends(get_db)):
    """Get the job by the given id."""
    db_job = crud.get_job(db=db, job_id=job_id)
    if db_job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    s_job = schemas.Job.from_orm(db_job)
    return s_job.dict()


@app.head("/jobs/{job_id}")
def head_job(job_id: int, response: Response, db: Session = Depends(get_db)):
    """Respond for a query about a job with the given id."""
    db_job = crud.get_job(db=db, job_id=job_id)
    if db_job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    last_modified = db_job.updated.replace(tzinfo=timezone.utc).strftime("%a, %d %b %Y %H:%M:%S %z")
    headers = {'Last-Modified': last_modified}
    return Response(headers=headers)


@app.delete("/jobs/{job_id}", status_code=204)
def delete_job(job_id: int, db: Session = Depends(get_db)):
    """Delete the job with the given id."""
    db_job = crud.get_job(db=db, job_id=job_id)
    if db_job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    crud.delete_job(db=db, job=db_job)


if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)