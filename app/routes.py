# routes.py
from flask import session, render_template, flash, redirect, url_for, request, jsonify, json, make_response, after_this_request
from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap
from werkzeug.urls import url_parse
from app.models import ShopName, Member, Course,CourseOffering,CourseEnrollee,\
ControlVariables, MemberTransactions, Term

from app import app
from app import db
from sqlalchemy import func, case, desc, extract, select, update, text
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, DBAPIError

import datetime as dt
from datetime import date, datetime, timedelta
from pytz import timezone

from flask_mail import Mail, Message

mail=Mail(app)
def logChange(staffID,colName,memberID,newData,origData):
    if staffID == None:
        staffID = '111111'
    if staffID == '':
        staffID = '111111'

    # Write data changes to tblMember_Data_Transactions
    est = timezone('EST')
    newTransaction = MemberTransactions(
        Transaction_Date = datetime.now(est),
        Member_ID = memberID,
        Staff_ID = staffID,
        Original_Data = origData,
        Current_Data = newData,
        Data_Item = colName,
        Action = 'UPDATE'
    )
    db.session.add(newTransaction)
    return
    db.session.commit()

@app.route('/', defaults={'villageID':None})
@app.route('/index/', defaults={'villageID':None})
@app.route('/index/<villageID>/')
@app.route("/classes",defaults={'villageID':None})
@app.route("/classes/<villageID>")
def index(villageID):
    
    #print('villageID - ',villageID)

    # GET TODAY'S DATE
    todays_date = date.today()
    todaySTR = todays_date.strftime('%m-%d-%Y')

    # PREPARE LIST OF MEMBER NAMES AND VILLAGE IDs
    # BUILD ARRAY OF NAMES FOR DROPDOWN LIST OF MEMBERS
    memberArray=[]
    sqlSelect = "SELECT Last_Name, First_Name, Nickname, Member_ID FROM tblMember_Data "
    sqlSelect += "ORDER BY Last_Name, First_Name "
    try:
        nameList = db.engine.execute(sqlSelect)
    except Exception as e:
        flash("Could not retrieve member list.","danger")
        return 'ERROR in member list function.'
    position = 0
    if nameList == None:
        flash('There is no one in the member table.','danger')
        return render_template("classes.html",members="",memberArray="")

    # NEED TO PLACE NAME IN AN ARRAY BECAUSE OF NEED TO CONCATENATE 
    for n in nameList:
        position += 1
        name = n.Last_Name + ', ' + n.First_Name
        if n.Nickname != None and n.Nickname != '':
            name += ' (' + n.Nickname + ')'
        name += ' [' + n.Member_ID + ']'
        
        memberArray.append(name)
    # BUILD TERM ARRAY
    termArray = []
    termItem = []
    terms = db.session.query(Term).order_by(Term.Order_Of_Terms.desc())    
    for t in terms:
        if t.Allow_Enrollment == True:
            allow = 'Ok'
        else:
            allow = ''
        termItem = {
            'termName':t.Course_Term,
            'allow':allow
        }
        termArray.append(termItem)

    # BUILD COURSE LIST
    courseArray = []
    courses = db.session.query(Course).order_by(Course.Course_Number).all()
    if courses == None:
        flash('There are no courses to list.','danger')
        return render_template("classes.html",memberID="",memberArray=memberArray,courseArray='')
    
    for c in courses:
        courseLine = c.Course_Number + ' - ' + c.Course_Title
        courseArray.append(courseLine)

    # IF A VILLAGE ID WAS NOT PASSED IN, DISPLAY THE classes.html FORM WITHOUT DATA
    if villageID == None:
         return render_template("classes.html",memberID="",memberArray=memberArray,\
         termArray=termArray,courseArray=courseArray)
    
    # IF A VILLAGE ID WAS PASSED IN ...
    member = db.session.query(Member).filter(Member.Member_ID == villageID).first()
    #print('Name - ',member.Last_Name)
    if member == None:
        memberName = ''
    else:
        memberName = member.First_Name
        if member.Nickname != None and member.Nickname != '':
            memberName += ' (' + member.Nickname + ')'
        memberName += ' ' + member.Last_Name

    # DISPLAY THE COURSES TAKEN DATA FOR THAT VILLAGE ID
    # SQL APPROACH
    sql = "SELECT tblCourse_Enrollees.ID AS Enrollee_Record_ID, tblCourse_Enrollees.Course_Term AS Course_Term, "
    sql += "tblCourse_Enrollees.Course_Number AS Course_Number, "
    sql += "tblCourse_Enrollees.Section_ID, tblCourse_Enrollees.Supply_Sets, tblCourses.Course_Title AS Course_Title, "
    sql += "tblCourse_Enrollees.Member_ID AS Student_ID, tblMember_Data.Last_Name AS Student_Last_Name, "
    sql += "tblMember_Data.First_Name AS Student_First_Name, tblMember_Data.NickName as Student_NickName, "
    sql += "tblCourse_Offerings.Section_Dates as Section_Dates, tblCourse_Offerings.Section_Dates_Note as Section_Note, "
    sql += "tblMember_Data_1.Last_Name AS Instructor_Last_Name, "
    sql += "tblMember_Data_1.First_Name AS Instructor_First_Name, tblMember_Data_1.NickName AS Instructor_NickName, "
    sql += "tblCourse_Enrollees.Date_Enrolled AS Date_Enrolled, tblCourse_Enrollees.Receipt_Number AS Receipt_Number, "
    sql += "tblCourse_Offerings.Section_ID AS Section_ID, tblCourse_Offerings.Section_Dates_Note AS Section_Notes "
    sql += "FROM tblCourses INNER JOIN (((tblCourse_Enrollees INNER JOIN tblCourse_Offerings "
    sql += "ON (tblCourse_Offerings.Course_Number = tblCourse_Enrollees.Course_Number) "
    sql += "AND (tblCourse_Offerings.Course_Term = tblCourse_Enrollees.Course_Term) "
    sql += "AND (tblCourse_Enrollees.Section_ID = tblCourse_Offerings.Section_ID)) "
    sql += "LEFT JOIN tblMember_Data ON tblCourse_Enrollees.Member_ID = tblMember_Data.Member_ID) "
    sql += "LEFT JOIN tblMember_Data AS tblMember_Data_1 ON tblCourse_Offerings.Instructor_ID = tblMember_Data_1.Member_ID) "
    sql += "ON tblCourses.Course_Number = tblCourse_Offerings.Course_Number "
    sql += "WHERE tblCourse_Enrollees.Member_ID = '" + villageID + "' "
    sql += "ORDER BY Course_Term desc, tblCourse_Enrollees.Course_Number, tblCourse_Enrollees.Section_ID"
    coursesTaken = db.session.execute(sql)
    
    coursesTakenDict = []
    coursesTakenItem = []

    for c in coursesTaken:
        if c.Instructor_Last_Name == None or c.Instructor_Last_Name == '':
            instructor = ''
        else:
            instructor = c.Instructor_Last_Name + ', ' + c.Instructor_First_Name
            if c.Instructor_NickName != None and c.Instructor_NickName != '':
                instructor += " (" + c.Instructor_NickName + ")"
        if c.Section_Dates == None:
            sectionDates = ''
        else:
            sectionDates = c.Section_Dates
        if c.Supply_Sets == None:
            supplySets = ''
        else:
            supplySets = c.Supply_Sets

        #print(c.Course_Term, c.Course_Number, c.Course_Title, sectionDates, c.Section_Note, instructor, c.Receipt_Number,supplySets)

        coursesTakenItem = {
            'term':c.Course_Term,
            'courseNum':c.Course_Number + c.Section_ID,
            'title':c.Course_Title,
            'dates':sectionDates,
            'times':c.Section_Note,
            'instructor':instructor,
            'receipt':c.Receipt_Number,
            'sets':supplySets
        }
        coursesTakenDict.append(coursesTakenItem)

    # SQLALCHEMY APPROACH
    # scheduleDict = []
    # scheduleItem = []
    # coursesTaken = db.session.query(CourseEnrollee)\
    #     .filter(CourseEnrollee.Member_ID == villageID)\
    #     .order_by(CourseEnrollee.Course_Term,CourseEnrollee.Course_Number).all()
    # if coursesTaken != None:
    #     for t in coursesTaken:
    #         title = db.session.query(Course.Course_Title).filter(Course.Course_Number == t.Course_Number).scalar()
    #         section = db.session.query(CourseOffering)\
    #             .filter(CourseOffering.Course_Number == t.Course_Number)\
    #             .filter(CourseOffering.Section_ID == t.Section_ID)\
    #             .filter(CourseOffering.Course_Term == t.Course_Term).first()
    #         instructor = db.session.query(Member).filter(Member.Member_ID == section.Instructor_ID).first()
    #         if instructor == None:
    #             instructorName = ''
    #         else:
    #             instructorName = instructor.Last_Name + ', ' + instructor.First_Name
    #         scheduleItem = {
    #             'term':t.Course_Term,
    #             'courseNum':t.Course_Number,
    #             'title':title,
    #             'dates':section.Section_Dates,
    #             'instructor':instructorName,
    #             'receipt':t.Receipt_Number,
    #             'sets':t.Supply_Sets
    #         }
    #         scheduleDict.append(scheduleItem)
    #     else:
    #         scheduleItem = {
    #             'title':'No classes taken.'
    #         }
    #         scheduleDict.append(scheduleItem)
  
    #print ('name - ', memberName)
    return render_template("classes.html",memberID=villageID,memberArray=memberArray,\
    todaySTR=todaySTR,termArray=termArray,courseArray=courseArray,\
    memberName=memberName,scheduleDict=coursesTakenDict)


