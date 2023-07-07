from os import name
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional, Generator, Dict, Any, Tuple
from csv import DictWriter
import io
# import pandas as pd

import models, schemas

def unwind(doc: Dict[str, Any]) -> Generator[Dict[str, Any], None, None]:
    '''
    Generates a dictionary for each value in the list of values of every key
    in the given dictionary
    '''
    if isinstance(doc, dict):
        has_array = False
        f_doc = doc.copy()
        for k in doc:
            if isinstance(doc[k], list):
                has_array = True
                head = doc[k][0] if len(doc[k])>0 else None
                tail = doc[k][1:] if len(doc[k])>1 else None
                f_doc[k] = head
                # unwind with the first element on this list
                yield from unwind(f_doc)
                if tail is not None:
                    # unwind with the rest of the list
                    f_doc[k] = tail
                    yield from unwind(f_doc)
                break
        if not has_array:
            # yield only if there was no list value
            # otherwise we ll be returning same dict more than once
            yield f_doc

def flatten_aux(doc: Dict[str, Any]) -> Generator[Tuple[str, Any], None, None]:
    '''
    Generate key, value pairs, where key is the combination of ancestor keys
    '''
    for key in doc:
        if isinstance(doc[key], dict):
            for k, v in flatten(doc[key]).items():
                yield (key+'_'+k, v)
        elif isinstance(doc[key], list):
            for item in doc[key]:
                if isinstance(item, dict):
                    for k, v in flatten_aux(item):
                        yield (key+'_'+k, v)
                else:
                    yield (key, item)
        else:
            yield (key, doc[key])
                

def flatten(doc: Dict[str, Any]) -> Dict[str, Any]:
    '''
    Flatten the given dictionary combining keys
    '''
    result = {}
    for key, value in flatten_aux(doc):
        if key in result:
            if not isinstance(result[key], list):
                result[key] = [result[key]]
            result[key].append(value)
        else:
            result[key] = value
    return result


def get_salary_by_value(db: Session, minimum: int, maximum: int) -> Optional[models.Salary]:
    '''
    Get the salary object from the database by giving the range of values
    '''
    return db.query(models.Salary).filter(
        and_(models.Salary.minimum==minimum, 
             models.Salary.maximum==maximum)
    ).one_or_none()

def create_salary(db: Session, salary: schemas.Salary) -> models.Salary:
    '''
    Create a salary object and insert it in the database
    '''
    db_salary = models.Salary(minimum=salary.minimum, maximum=salary.maximum)
    db.add(db_salary)
    db.commit()
    db.refresh(db_salary)
    return db_salary

def get_location_by_coords(db: Session, latitude: float, longitude: float) -> Optional[models.Location]:
    '''
    Retrieve a location object from the database by providing coordinates
    '''
    return db.query(models.Location).filter(
        and_(models.Location.latitude==latitude,
             models.Location.longitude==longitude)
    ).one_or_none()

def create_location(db: Session, location: schemas.Location) -> models.Location:
    '''
    Create a Location object and insert it in the database
    '''
    db_location = models.Location(**(location.dict()))
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location

def get_exprerience_by_name(db: Session, name: str) -> Optional[models.Experience]:
    '''
    Retrieve an Experience object from the database
    '''
    return db.query(models.Experience).filter(
        models.Experience.name==name
    ).one_or_none()

def create_experience(db: Session, experience: str) -> models.Experience:
    '''
    Create an Experience object and insert it in the database
    '''
    db_experience = models.Experience(name=experience)
    db.add(db_experience)
    db.commit()
    db.refresh(db_experience)
    return db_experience

def get_industry_by_name(db: Session, name: str) -> Optional[models.Industry]:
    '''
    Retrieve an Industry object from the database
    '''
    return db.query(models.Industry).filter(
        models.Industry.name==name
    ).one_or_none()

def create_industry(db: Session, industry: str) -> models.Industry:
    '''
    Create an Industry object and insert it in the database
    '''
    db_industry = models.Industry(name=industry)
    db.add(db_industry)
    db.commit()
    db.refresh(db_industry)
    return db_industry

def get_company_by_name_url(db: Session, name: str, url: str) -> Optional[models.Company]:
    '''
    Retrieve a company object from the database
    '''
    return db.query(models.Company).filter(
        and_(models.Company.name==name,
             models.Company.url==url)
    ).one_or_none()

def create_company(db: Session, company: schemas.Company) -> models.Company:
    '''
    Create a Company object and insert it in the database
    '''
    industries = []
    if company.industries is not None:
        # industries = []
        for industry in company.industries:
            db_industry = get_industry_by_name(db=db, name=industry)
            if db_industry is None:
                db_industry = create_industry(db=db, industry=industry)
            industries.append(db_industry)
    db_company = models.Company(name=company.name,
                                url=company.url,
                                size=company.size,
                                company_type=company.company_type,
                                company_industries=industries)
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company

def get_role_by_name(db: Session, name: str) -> Optional[models.Role]:
    '''
    Retrieve a Role object from the database
    '''
    return db.query(models.Role).filter(
        models.Role.name==name
    ).one_or_none()

def create_role(db: Session, role: str) -> models.Role:
    '''
    Create a Role object and insert it in the database
    '''
    db_role = models.Role(name=role)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

def get_job_type_by_name(db: Session, name: str) -> Optional[models.JobType]:
    '''
    Retrieve a JobType object from the database
    '''
    return db.query(models.JobType).filter(
        models.JobType.name==name
    ).one_or_none()

def create_job_type(db: Session, job_type: str) -> models.JobType:
    '''
    Create a JobType object and insert it in the database
    '''
    db_job_type = models.JobType(name=job_type)
    db.add(db_job_type)
    db.commit()
    db.refresh(db_job_type)
    return db_job_type

def get_skill_by_name(db: Session, name: str) -> Optional[models.Skill]:
    '''
    Retrieve a Skill object from the database
    '''
    return db.query(models.Skill).filter(
        models.Skill.name==name
    ).one_or_none()

def create_skill(db: Session, skill: str) -> models.Skill:
    '''
    Create a Skill object and insert it in the database
    '''
    db_skill = models.Skill(name=skill)
    db.add(db_skill)
    db.commit()
    db.refresh(db_skill)
    return db_skill

def get_technology_by_name(db: Session, name: str) -> Optional[models.Technology]:
    '''
    Retrieve a Technology object from the database
    '''
    return db.query(models.Technology).filter(
        models.Technology.name==name
    ).one_or_none()

def create_technology(db: Session, technology: str) -> models.Technology:
    '''
    Create a Technology object and insert it in the database
    '''
    db_technology = models.Technology(name=technology)
    db.add(db_technology)
    db.commit()
    db.refresh(db_technology)
    return db_technology

def get_joel_test_by_name(db: Session, name: str) -> Optional[models.JoelTest]:
    '''
    Retrieve a JoelTest object from the database
    '''
    return db.query(models.JoelTest).filter(
        models.JoelTest.name==name
    ).one_or_none()

def create_joel_test(db: Session, joel_test: str) -> models.JoelTest:
    '''
    Create a JoelTest object and insert it in the database
    '''
    db_joel_test = models.JoelTest(name=joel_test)
    db.add(db_joel_test)
    db.commit()
    db.refresh(db_joel_test)
    return db_joel_test

def get_remote_by_name(db: Session, name: str) -> Optional[models.Remote]:
    '''
    Retrieve a Remote object from the database
    '''
    return db.query(models.Remote).filter(
        models.Remote.name==name
    ).one_or_none()

def create_remote(db: Session, remote: str) -> models.Remote:
    '''
    Create a Remote object and insert it in the database
    '''
    db_remote = models.Remote(name=remote)
    db.add(db_remote)
    db.commit()
    db.refresh(db_remote)
    return db_remote

def get_benefit_by_name(db: Session, name: str) -> Optional[models.Benefit]:
    '''
    Retrieve a Benefit object from the database
    '''
    return db.query(models.Benefit).filter(
        models.Benefit.name==name
    ).one_or_none()

def create_benefit(db: Session, benefit: str) -> models.Benefit:
    '''
    Create a Benefit object and insert it in the database
    '''
    db_benefit = models.Benefit(name=benefit)
    db.add(db_benefit)
    db.commit()
    db.refresh(db_benefit)
    return db_benefit

def get_job(db: Session, job_id: int) -> Optional[models.Job]:
    '''
    Retrieve a Job object with the give id from the database
    '''
    return db.query(models.Job).filter(models.Job.id==job_id).one_or_none()

def get_job_by_url(db: Session, url: str) -> Optional[models.Job]:
    '''
    Retrieve a Job object with the given url from the database
    '''
    return db.query(models.Job).filter(models.Job.url==url).one_or_none()

def get_jobs(db: Session, offset: int=0, limit: Optional[int]=None) -> List[models.Job]:
    '''
    Retrieve a list of Job documents from the database
    '''
    q = db.query(models.Job).offset(offset)
    if limit is not None:
        return q.limit(limit).all()
    else:
        return q.all()
    # return db.query(models.Job).offset(offset).limit(limit).all()

def create_or_update_job(db: Session, job: schemas.Job) -> models.Job:
    '''
    Given a job schema, create a Job object in the database or update a
    Job object from the database if such one already exists with the given id
    from the schema
    '''
    # get employer
    db_company = None
    if job.employer is not None:
        db_company = get_company_by_name_url(
            db=db, name=job.employer.name, url=job.employer.url)
        if db_company is None:
            db_company = create_company(db=db, company=job.employer)
    # get location
    db_location = None
    if job.location is not None:
        db_location = get_location_by_coords(
            db=db,
            latitude=job.location.latitude,
            longitude=job.location.longitude)
            # country_code=job.location.country_code)
        if db_location is None:
            db_location = create_location(db=db, location=job.location)
    # get salary
    db_salary = None
    if job.salary is not None:
        db_salary = get_salary_by_value(
            db=db, minimum=job.salary.minimum, maximum=job.salary.maximum)
        if db_salary is None:
            db_salary = create_salary(db=db, salary=job.salary)
    # get roles
    db_roles = []
    if job.roles is not None:
        # db_roles = []
        for role in job.roles:
            db_role = get_role_by_name(db=db, name=role)
            if db_role is None:
                db_role = create_role(db=db, role=role)
            db_roles.append(db_role)
    # get experience
    db_experience = []
    if job.experience is not None:
        # db_experience = []
        for experience in job.experience:
            db_exp = get_exprerience_by_name(db=db, name=experience)
            if db_exp is None:
                db_exp = create_experience(db=db, experience=experience)
            db_experience.append(db_exp)
    # get job type
    db_job_types = []
    if job.job_types is not None:
        # db_job_types = []
        for job_type in job.job_types:
            db_job_type = get_job_type_by_name(db=db, name=job_type)
            if db_job_type is None:
                db_job_type = create_job_type(db=db, job_type=job_type)
            db_job_types.append(db_job_type)
    # get skill
    db_skills = []
    if job.skills is not None:
        # db_skills = []
        for skill in job.skills:
            db_skill = get_skill_by_name(db=db, name=skill)
            if db_skill is None:
                db_skill = create_skill(db=db, skill=skill)
            db_skills.append(db_skill)
    # get technology
    db_technologies = []
    if job.technologies is not None:
        # db_technologies = []
        for tech in job.technologies:
            db_tech = get_technology_by_name(db=db, name=tech)
            if db_tech is None:
                db_tech = create_technology(db=db, technology=tech)
            db_technologies.append(db_tech)
    # get joel test
    db_joel_tests = []
    if job.joel_test is not None:
        # db_joel_tests = []
        for joel_test in job.joel_test:
            db_joel_test = get_joel_test_by_name(db=db, name=joel_test)
            if db_joel_test is None:
                db_joel_test = create_joel_test(db=db, joel_test=joel_test)
            db_joel_tests.append(db_joel_test)
    # get remote (cannot be None)
    db_remotes = []
    for remote in job.remote:
        db_remote = get_remote_by_name(db=db, name=remote)
        if db_remote is None:
            db_remote = create_remote(db=db, remote=remote)
        db_remotes.append(db_remote)
    # get benefits
    db_benefits = []
    if job.benefits is not None:
        for benefit in job.benefits:
            db_benefit = get_benefit_by_name(db=db, name=benefit)
            if db_benefit is None:
                db_benefit = create_benefit(db=db, benefit=benefit)
            db_benefits.append(db_benefit)

    # check if job exists
    db_job = db.query(models.Job).filter(models.Job.id==job.id).one_or_none()

    if db_job is None:
        # create job
        db_job = models.Job(id = job.id)
        db.add(db_job)
    db_job.title = job.title
    db_job.url = job.url
    db_job.description = job.description
    db_job.visa = job.visa
    db_job.relocation = job.relocation
    db_job.created = job.created
    db_job.updated = job.updated
    db_job.equity = job.equity
    db_job.employer = db_company
    db_job.job_roles = db_roles
    db_job.job_skills = db_skills
    db_job.job_experiences = db_experience
    db_job.salary = db_salary
    db_job.location = db_location
    db_job.job_job_types = db_job_types
    db_job.job_technologies = db_technologies
    db_job.job_joel_tests = db_joel_tests
    db_job.job_remotes = db_remotes
    db.commit()
    db.refresh(db_job)
    return db_job

def get_jobs_csv(jobs: List[models.Job]) -> Generator[str, None, None]:
    '''
    Given a list of Job database objects, generates rows of comma separated values
    '''
    f = io.StringIO()
    fieldnames = ['id', 'title', 'technologies',
                    'employer_name', 'employer_size',
                    'employer_industries', 'employer_company_type',
                    'experience', 'roles', 'job_types',
                    'joel_test', 'skills', 'created',
                    'location_longitude', 'location_latitude',
                    'salary_minimum', 'salary_maximum',
                    'visa', 'equity', 'relocation',
                    'benefits', 'remote']
    dw = DictWriter(f, fieldnames, extrasaction='ignore')
    dw.writeheader()
    yield f.getvalue()
    for job in jobs:
        for row in unwind(flatten(schemas.Job.from_orm(job).dict())):
            f = io.StringIO()
            dw = DictWriter(f, fieldnames, extrasaction='ignore')
            dw.writerow(row)
            yield f.getvalue()

def delete_job(db: Session, job: models.Job) -> None:
    '''
    Delete the job object from the database
    '''
    db.delete(job)
    db.commit()
