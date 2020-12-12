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
    print('villageID - ',villageID)
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
    member = db.session.query(Member).filter_by(Member.Member_ID == villageID).first()
    print('Name - ',member.Last_Name)
    if member == None:
        memberName = ''
    else:
        memberName = member.First_Name
        if memberName != None:
            memberName += ' (' + member.Nickname + ')'
        memberName += member.Last_Name

    # DISPLAY THE COURSES TAKEN DATA FOR THAT VILLAGE ID
    sqlCoursesTaken = "SELECT "
    # if (applicant == None):
    #     msg = "No record for applicant with village ID " + villageID
    #     flash(msg,"info")
    #     return render_template("classes.html",applicant='',memberArray=memberArray,todaySTR=todaySTR)
    # else:
        # DETERMINE APPLICANTS PLACE ON WAITING LIST
        # RETURN COUNT OF # OF RECORDS BEFORE THEIR ID WHEN ORDERED BY ID AND FILTERED BY PlannedCertificationDate is null and NoLongerInterested isnull 
        # placeOnList = 0 
        # placeOnList = db.session.query(func.count(classes.MemberID)).filter(classes.PlannedCertificationDate == None) \
        #     .filter(classes.NoLongerInterested == None) \
        #     .filter(classes.id < applicant.id) \
        #     .scalar() 
    return render_template("classes.html",memberID=memberID,memberArray=memberArray,\
    todaySTR=todaySTR,termArray=termArray,courseArray=courseArray,\
    memberName=memberName)


