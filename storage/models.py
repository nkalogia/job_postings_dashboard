import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.ext.associationproxy import association_proxy
from database import Base

class SurrogatePK:
    id = sa.Column(sa.Integer, primary_key=True)

job_remote = sa.Table(
    'job_remote', Base.metadata,
    sa.Column('job_id', sa.Integer, sa.ForeignKey('job.id')),
    sa.Column('remote_id', sa.Integer, sa.ForeignKey('remote.id')))


job_experience = sa.Table(
    'job_experience', Base.metadata,
    sa.Column('job_id', sa.Integer, sa.ForeignKey('job.id')),
    sa.Column('experience_id', sa.Integer, sa.ForeignKey('experience.id')))

job_job_type = sa.Table(
    'job_job_type', Base.metadata,
    sa.Column('job_id', sa.Integer, sa.ForeignKey('job.id')),
    sa.Column('job_type_id', sa.Integer, sa.ForeignKey('job_type.id')))

job_role = sa.Table(
    'job_role', Base.metadata,
    sa.Column('job_id', sa.Integer, sa.ForeignKey('job.id')),
    sa.Column('role_id', sa.Integer, sa.ForeignKey('role.id')))

job_technology = sa.Table(
    'job_technology', Base.metadata,
    sa.Column('job_id', sa.Integer, sa.ForeignKey('job.id')),
    sa.Column('technology_id', sa.Integer, sa.ForeignKey('technology.id')))

job_skill = sa.Table(
    'job_skill', Base.metadata,
    sa.Column('job_id', sa.Integer, sa.ForeignKey('job.id')),
    sa.Column('skill_id', sa.Integer, sa.ForeignKey('skill.id')))

job_joel_test = sa.Table(
    'job_joel_test', Base.metadata,
    sa.Column('job_id', sa.Integer, sa.ForeignKey('job.id')),
    sa.Column('joel_test_id', sa.Integer, sa.ForeignKey('joel_test.id')))

company_industry = sa.Table(
    'company_industry', Base.metadata,
    sa.Column('company_id', sa.Integer, sa.ForeignKey('company.id')),
    sa.Column('industry_id', sa.Integer, sa.ForeignKey('industry.id')))

company_benefit = sa.Table(
    'company_benefit', Base.metadata,
    sa.Column('company_id', sa.Integer, sa.ForeignKey('company.id')),
    sa.Column('benefit_id', sa.Integer, sa.ForeignKey('benefit.id')))


class Job(Base, SurrogatePK):
    __tablename__ = 'job'
    url = sa.Column(sa.String, unique=True)
    title = sa.Column(sa.String)
    employer_id = sa.Column(sa.Integer, sa.ForeignKey('company.id'))
    employer = orm.relationship('Company', back_populates='jobs')
    location_id = sa.Column(sa.Integer, sa.ForeignKey('location.id'))
    location = orm.relationship('Location', 
                                back_populates='jobs')
    equity = sa.Column(sa.Boolean)
    salary_id = sa.Column(sa.Integer, sa.ForeignKey('salary.id'))
    salary = orm.relationship('Salary', 
                              back_populates='jobs')
    visa = sa.Column(sa.Boolean)
    relocation = sa.Column(sa.Boolean)
    remote = association_proxy('job_remotes', 'name')
    experience = association_proxy('job_experiences', 'name')
    job_types = association_proxy('job_job_types', 'name')
    roles = association_proxy('job_roles', 'name')
    technologies = association_proxy('job_technologies', 'name')
    skills = association_proxy('job_skills', 'name')
    joel_test = association_proxy('job_joel_tests', 'name')

    # experience = orm.relationship('Experience',
    #                               secondary=job_experience,
    #                               back_populates='jobs')
    # job_types = orm.relationship('JobType',
    #                              secondary=job_job_type,
    #                              back_populates='jobs')
    # roles = orm.relationship('Role',
    #                          secondary=job_role,
    #                          back_populates='jobs')
    # technologies = orm.relationship('Technology',
    #                                 secondary=job_technology,
    #                                 back_populates='jobs')                    
    # skills = orm.relationship('Skill',
    #                           secondary=job_skill,
    #                           back_populates='jobs')    
    # joel_test = orm.relationship('JoelTest',
    #                              secondary=job_joel_test,
    #                              back_populates='jobs')
    description = sa.Column(sa.String)
    created = sa.Column(sa.DateTime)
    updated = sa.Column(sa.DateTime)
    

class Company(Base, SurrogatePK):
    __tablename__ = 'company'
    url = sa.Column(sa.String)
    name = sa.Column(sa.String)
    jobs = orm.relationship('Job', back_populates='employer')
    industries = association_proxy('company_industries', 'name')
    # industries = orm.relationship('Industry',
    #                               secondary=company_industry,
    #                               back_populates='companies')
    size = sa.Column(sa.String)
    company_type = sa.Column(sa.String)
    benefit_id = sa.Column(sa.Integer, sa.ForeignKey('benefit.id'))
    benefits = association_proxy('company_benefits', 'name')
    # benefits = orm.relationship('Benefit', back_populates='companies')
    __table_args__ = (sa.UniqueConstraint('name', 'url', name='name_url_unique'),)


class Location(Base, SurrogatePK):
    __tablename__ = 'location'
    latitude = sa.Column(sa.Float)
    longitude = sa.Column(sa.Float)
    country_code = sa.Column(sa.String)
    jobs = orm.relationship('Job', back_populates='location')
    __table_args__ = (sa.UniqueConstraint('latitude', 'longitude', name='latitude_longitude_unique'),)

class Remote(Base, SurrogatePK):
    __tablename__ = 'remote'
    name = sa.Column(sa.String, unique=True)
    jobs = orm.relationship('Job',
                            secondary=job_remote,
                            backref='job_remotes')

class Salary(Base, SurrogatePK):
    __tablename__ = 'salary'
    minimum = sa.Column(sa.Integer)
    maximum = sa.Column(sa.Integer)
    jobs = orm.relationship('Job', back_populates='salary')
    __table_args__ = (sa.UniqueConstraint('minimum', 'maximum', name='minimum_maximum_unique'),)

class Experience(Base, SurrogatePK):
    __tablename__ = 'experience'
    name = sa.Column(sa.String, unique=True)
    jobs = orm.relationship('Job',
                            secondary=job_experience,
                            backref='job_experiences')

class JobType(Base, SurrogatePK):
    __tablename__ = 'job_type'
    name = sa.Column(sa.String, unique=True)
    jobs = orm.relationship('Job',
                            secondary=job_job_type,
                            backref='job_job_types')

class Role(Base, SurrogatePK):
    __tablename__ = 'role'
    name = sa.Column(sa.String, unique=True)
    jobs = orm.relationship('Job',
                            secondary=job_role,
                            backref='job_roles')

class Technology(Base, SurrogatePK):
    __tablename__ = 'technology'
    name = sa.Column(sa.String, unique=True)
    jobs = orm.relationship('Job',
                            secondary=job_technology,
                            backref='job_technologies')

class Skill(Base, SurrogatePK):
    __tablename__ = 'skill'
    name = sa.Column(sa.String, unique=True)
    description = sa.Column(sa.String)
    jobs = orm.relationship('Job',
                            secondary=job_skill,
                            backref='job_skills')

class JoelTest(Base, SurrogatePK):
    __tablename__ = 'joel_test'
    name = sa.Column(sa.String, unique=True)
    jobs = orm.relationship('Job',
                            secondary=job_joel_test,
                            backref='job_joel_tests')

class Industry(Base, SurrogatePK):
    __tablename__ = 'industry'
    name = sa.Column(sa.String, unique=True)
    companies = orm.relationship('Company',
                                 secondary=company_industry,
                                 backref='company_industries')

class Benefit(Base, SurrogatePK):
    __tablename__ = 'benefit'
    name = sa.Column(sa.String, unique=True)
    companies = orm.relationship('Company', 
                                 secondary=company_benefit,
                                 backref='company_benefits')
