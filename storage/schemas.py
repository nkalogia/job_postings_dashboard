from __future__ import annotations
from typing import List, Optional, Union
from pydantic import BaseModel
from sqlalchemy.ext.associationproxy import _AssociationList
from datetime import datetime

class MyCollection(_AssociationList, list):
    '''
    A custom collection to provide type checking through pydantic for 
    both a list and an _AssociationList
    '''
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        if isinstance(value, _AssociationList):
            return [name for name in value]
        if isinstance(value, list):
            return value
        else:
            raise TypeError("AssociationList or List required")

class Job(BaseModel):
    id: int
    url: str
    title: str
    employer: Optional[Company]
    location: Optional[Location]
    remote: MyCollection
    equity: bool
    salary: Optional[Salary]
    visa: bool
    relocation: bool
    experience: Optional[MyCollection]
    job_types: Optional[MyCollection]
    roles: Optional[MyCollection]
    technologies: Optional[MyCollection]
    skills: Optional[MyCollection]
    joel_test: Optional[MyCollection]
    benefits: Optional[MyCollection]
    description: Optional[str]
    created: datetime
    updated: datetime

    class Config:
        orm_mode=True
        arbitrary_types_allowed = True

class Company(BaseModel):
    url: Optional[str]
    name: str
    industries: Optional[MyCollection]
    size: Optional[str]
    company_type: Optional[str]
    benefits: Optional[MyCollection]

    class Config:
        orm_mode=True
        arbitrary_types_allowed=True

class Location(BaseModel):
    latitude: float
    longitude: float
    country_code: Optional[str]
    # jobs: Optional[List[Job]]

    class Config:
        orm_mode=True

class Salary(BaseModel):
    minimum: int
    maximum: int
    # jobs: Optional[List[Job]]

    class Config:
        orm_mode=True

class JobType(BaseModel):
    name: str
    jobs: Optional[List[Job]]

    class Config:
        orm_mode=True

class Role(BaseModel):
    name: str
    jobs: Optional[List[Job]]

    class Config:
        orm_mode=True

class Experience(BaseModel):
    name: str
    jobs: Optional[List[Job]]

    class Config:
        orm_mode=True

class Skill(BaseModel):
    name: str
    jobs: Optional[List[Job]]

    class Config:
        orm_mode=True

class Technology(BaseModel):
    name: str
    jobs: Optional[List[Job]]

    class Config:
        orm_mode=True

class JoelTest(BaseModel):
    name: str
    jobs: Optional[List[Job]]

    class Config:
        orm_mode=True

class Industry(BaseModel):
    name: str
    companies: Optional[List[Company]]

    class Config:
        orm_mode=True

class Benefit(BaseModel):
    name: str
    companies: Optional[List[Company]]

    class Config:
        orm_mode=True

class Remote(BaseModel):
    name: str
    jobs: Optional[List[Job]]

    class Config:
        orm_mode=True

Job.update_forward_refs()
Company.update_forward_refs()
