# models.py 

from datetime import datetime 
from time import time
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import select, func, Column, extract, ForeignKey
from sqlalchemy.orm import column_property, relationship
from sqlalchemy.ext.hybrid import hybrid_property
from app import app
    
class ControlVariables(db.Model):
    __tablename__ = 'tblControl_Variables'
    __table_args__ = {"schema": "dbo"}
    Shop_Number = db.Column(db.Integer, primary_key=True)
    Current_Dues_Year = db.Column(db.String(4))
    Current_Dues_Amount = db.Column(db.Numeric)
    Current_Initiation_Fee = db.Column(db.Numeric)
    Date_To_Begin_New_Dues_Collection = db.Column(db.Date)
    Date_To_Accept_New_Members = db.Column(db.Date)
    Last_Acceptable_Monitor_Training_Date = db.Column(db.Date)
    AcceptingNewMembers = db.Column(db.Boolean)
    Current_Course_Term = db.Column(db.String(15))
    Repeat_Classes_Allowed_Date = db.Column(db.Date)
    More_Than_2_Classes_Allowed_Date = db.Column(db.Date)
    Dues_Account = db.Column(db.String(10))
    Initiation_Fee_Account = db.Column(db.String(10))
    WaitingListApplicantNote = db.Column(db.String(255))

class Member(db.Model):
    __tablename__ = 'tblMember_Data'
    __table_args__ = {"schema": "dbo"}
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    Member_ID = db.Column(db.String(6),
         index=True,
         unique=True)
    Last_Name = db.Column(db.String(25))
    First_Name = db.Column(db.String(25))
    Middle_Name = db.Column(db.String(25))
    Nickname = db.Column(db.String(25))
    Initials = db.Column(db.String(3))
    Date_Joined = db.Column(db.Date)
    Certified = db.Column(db.Boolean)
    Certification_Training_Date = db.Column(db.Date,nullable=True, default='')
    Certified_2 = db.Column(db.Boolean)
    Certification_Training_Date_2 = db.Column(db.Date)
    Address = db.Column(db.String(30))
    City = db.Column(db.String(25))
    State = db.Column(db.String(2))
    Zip = db.Column(db.String(10))
    Village = db.Column(db.String(30))

    Home_Phone = db.Column(db.String(14))
    Cell_Phone = db.Column(db.String(14))
    eMail = db.Column('E-Mail',db.String(50))
    Dues_Paid=db.Column(db.Boolean)
    NonMember_Volunteer=db.Column(db.Boolean)
    Restricted_From_Shop = db.Column(db.Boolean)
    Reason_For_Restricted_From_Shop = db.Column(db.String(255))
    Last_Monitor_Training = db.Column(db.Date)
    Deceased = db.Column(db.Boolean)
    Inactive = db.Column(db.Boolean)
    Inactive_Date = db.Column(db.Date)
    Villages_Waiver_Signed = db.Column(db.Boolean)
    Villages_Waiver_Date_Signed = db.Column(db.Date)
    Jan_resident = db.Column(db.Boolean)
    Feb_resident = db.Column(db.Boolean)
    Mar_resident = db.Column(db.Boolean)
    Apr_resident = db.Column(db.Boolean)
    May_resident = db.Column(db.Boolean)
    Jun_resident = db.Column(db.Boolean)
    Jul_resident = db.Column(db.Boolean)
    Aug_resident = db.Column(db.Boolean)
    Sep_resident = db.Column(db.Boolean)
    Oct_resident = db.Column(db.Boolean)
    Nov_resident = db.Column(db.Boolean)
    Dec_resident = db.Column(db.Boolean)

    Alt_Address = db.Column(db.String(30))
    Alt_City = db.Column(db.String(25))
    Alt_State = db.Column(db.String(2))
    Alt_Zip = db.Column(db.String(10))
    Alt_Country = db.Column(db.String(30))
    Alt_Phone = db.Column(db.String(14))
    
    Emerg_Name = db.Column(db.String(30))
    Emerg_Phone = db.Column(db.String(14))
    Emerg_Pacemaker = db.Column(db.Boolean)
    Emerg_Stent = db.Column(db.Boolean)
    Emerg_CABG = db.Column(db.Boolean)
    Emerg_MI = db.Column(db.Boolean)
    Emerg_Other_Diagnosis = db.Column(db.String(50))
    Emerg_Diabetes_Type_1 = db.Column(db.Boolean)
    Emerg_Diabetes_Type_2 = db.Column(db.Boolean)
    Emerg_Diabetes_Other = db.Column(db.String(50))
    Emerg_Medical_Alergies = db.Column(db.String(255))
    Emerg_No_Data_Provided = db.Column(db.Boolean)
    Defibrillator_Trained = db.Column(db.Boolean)
    Monitor_Duty_Notes = db.Column(db.String(255))
    Requires_Tool_Crib_Duty = db.Column(db.Boolean)
    Member_Notes = db.Column(db.String(255))
    Monitor_Coordinator = db.Column(db.Boolean)
    Default_Type_Of_Work = db.Column(db.String(50))
    Skill_Level = db.Column(db.Integer)
    Monitor_Duty_Waiver_Reason = db.Column(db.String(50))
    Monitor_Duty_Waiver_Expiration_Date = db.Column(db.Date)
    
    Temporary_Village_ID = db.Column(db.Boolean)
    Temporary_ID_Expiration_Date = db.Column(db.Date)
    Last_Monitor_Training_Shop_2 = db.Column(db.Date)
    Monitor_Sub = db.Column(db.Boolean)
    Monitor_Sub_2 = db.Column(db.Boolean)
    
    isAskMe = db.Column(db.Boolean)
    Mentor = db.Column(db.Boolean)
    isBODmember = db.Column(db.Boolean)
    canSellMdse = db.Column(db.Boolean)
    Certification_Staff = db.Column(db.Boolean)
    Office_Staff = db.Column(db.Boolean)
    DBA = db.Column(db.Boolean)
    Monitor_Coordinator = db.Column(db.Boolean)
    Instructor = db.Column(db.Boolean)
    isPresident = db.Column(db.Boolean)
    canSellLumber = db.Column(db.Boolean)
    isSafetyCommittee = db.Column(db.Boolean)
    Maintenance = db.Column(db.Boolean)
    isSpecialProjects = db.Column(db.Boolean)
    Manager = db.Column(db.Boolean)
    isVP = db.Column(db.Boolean)
    LightspeedID = db.Column(db.String(20))
    fullName = column_property(First_Name + " " + Last_Name)
    # Relationships
    #activities = db.relationship('MemberActivity', backref='member')
    def wholeName(self):
        return self.lastName + ", " + self.firstName 

class Course(db.Model):
    __tablename__ = 'tblCourses'
    __table_args__ = {"schema": "dbo"}
    ID = db.Column(db.Integer,primary_key=True)
    Course_Number = db.Column(db.String(4))
    Course_Title = db.Column(db.String(50))
    Course_Fee = db.Column(db.Numeric)
    Course_Duration = db.Column(db.String(15))
    Course_Note = db.Column(db.String(255))
    Course_Suggested_Supplies = db.Column(db.String(50))
    Course_Suggested_Supply_Fee = db.Column(db.Numeric)
    Course_Description = db.Column(db.String(255))
    Course_Suggested_Size = db.Column(db.Integer)
    Course_Prerequisite = db.Column(db.String(50))
    Course_Supplies_Are_Taxable = db.Column(db.Boolean)

class CourseOffering(db.Model):
    __tablename__ = 'tblCourse_Offerings'
    __table_args__ = {"schema": "dbo"}
    ID = db.Column(db.Integer,primary_key=True)
    Course_Term = db.Column(db.String(15))
    Course_Number = db.Column(db.String(4))
    Section_ID = db.Column(db.String(1))
    Instructor_ID = db.Column(db.String(6))
    Section_Dates = db.Column(db.String(50))
    Section_Dates_Note = db.Column(db.String(30))
    Section_Size = db.Column(db.Integer)
    Prerequisite_Course = db.Column(db.String(4))
    Section_Supplies = db.Column(db.String(50))
    Section_Supplies_Fee = db.Column(db.Numeric)
    Section_Closed_Date = db.Column(db.Date)
    Section_Start_Date = db.Column(db.Date)

class CourseEnrollee(db.Model):
    __tablename__ = 'tblCourse_Enrollees'
    __table_args__ = {"schema": "dbo"}
    ID = db.Column(db.Integer,primary_key=True)
    Course_Term = db.Column(db.String(15))
    Course_Number = db.Column(db.String(4))
    Section_ID = db.Column(db.String(1))
    Member_ID = db.Column(db.String(6))
    Receipt_Number = db.Column(db.String(6))
    Date_Enrolled = db.Column(db.Date)
    Supply_Sets = db.Column(db.Integer)
    Prerequisite_Met_By = db.Column(db.String(50))
    Registered_By = db.Column(db.String(6))

class Term(db.Model):
    __tablename__ = 'tblValid_Course_Terms'
    __table_args__ = {"schema": "dbo"}
    Course_Term = db.Column(db.String(30),primary_key=True)
    Order_Of_Terms = db.Column(db.Integer)
    Allow_Enrollment = db.Column(db.Boolean)

class ShopName(db.Model):
    __tablename__ = 'tblShop_Names'
    __table_args__ = {"schema": "dbo"}
    Shop_Number = db.Column(db.Integer, primary_key=True)
    Shop_Name = db.Column(db.String(30))

class MemberTransactions(db.Model):
    __tablename__="tblMember_Data_Transactions"
    __table_args__={"schema":"dbo"}
    ID = db.Column(db.Integer, primary_key=True)
    Transaction_Date = db.Column(db.DateTime)
    Member_ID = db.Column(db.String(6))
    Staff_ID = db.Column(db.String(6))
    Original_Data = db.Column(db.String(50))
    Current_Data = db.Column(db.String(50))
    Data_Item = db.Column(db.String(30))
    Action = db.Column(db.String(6))
