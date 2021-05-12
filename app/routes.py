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

from sqlalchemy.sql import text as SQLQuery

import datetime as dt
from datetime import date, datetime, timedelta
from pytz import timezone

from flask_mail import Mail, Message

mail=Mail(app)


@app.route('/')
@app.route('/index/')
@app.route("/classes/")
def index():
    
    villageID = request.args.get('villageID')
    staffID = getStaffID()
   
    # GET TODAY'S DATE
    todays_date = date.today()
    todaySTR = todays_date.strftime('%m-%d-%Y')

    # IS USER A STAFF MEMBER, DBA, OR MANAGER
    isDBA = 'False'
    isMgr = 'False'
    staffName = ''
    if staffID != None:
        member = db.session.query(Member).filter(Member.Member_ID == staffID).first()
        if member != None:
            staffName = member.First_Name + ' ' + member.Last_Name
            if member.DBA:
                isDBA = 'True'
            if member.Manager:
                isMgr = 'True'

    # GET CONTROL VARIABLES
    controlVariables = db.session.query(ControlVariables).filter(ControlVariables.Shop_Number == 1).first()
    term = controlVariables.Current_Course_Term
    
    repeatClassesAllowedDateDAT = controlVariables.Repeat_Classes_Allowed_Date
    repeatClassesAllowedDateSTR = repeatClassesAllowedDateDAT.strftime('%m-%d-%Y')
    if repeatClassesAllowedDateDAT > todays_date:
        repeatClassesAllowed = 'False'
    else:
        repeatClassesAllowed = 'True'

    moreThan2ClassesAllowedDateDAT = controlVariables.More_Than_2_Classes_Allowed_Date
    moreThan2ClassesAllowedDateSTR = moreThan2ClassesAllowedDateDAT.strftime('%m-%d-%Y')
    if moreThan2ClassesAllowedDateDAT > todays_date:
        moreThan2ClassesAllowed = 'False'
    else:
        moreThan2ClassesAllowed = 'True'
    
    # SET VARIABLES INITIAL VALUES
    certificationStatus = ''
    enrollmentsThisTerm = 0

    
    # PREPARE LIST OF MEMBER NAMES AND VILLAGE IDs
    # BUILD ARRAY OF NAMES FOR DROPDOWN LIST OF MEMBERS
    memberArray=[]
    try:
        sp = "EXEC nameList"
        sql = SQLQuery(sp)
        nameList = db.engine.execute(sql)
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
    
    # STORED PROCEDURE FOR GETTING COURSES OFFERED THIS TERM
    sp = "EXEC coursesThisTerm '" + term + "'"
    sql = SQLQuery(sp)
    courses = db.engine.execute(sql)

    if courses == None: 
        flash('There are no courses to list.','danger')
        return render_template("classes.html",memberID="",memberArray=memberArray,courseArray='')

    for c in courses:
        courseLine = c.courseNumber + ' - ' + c.courseTitle
        courseArray.append(courseLine)


    # IF A VILLAGE ID WAS NOT PASSED IN, DISPLAY THE classes.html FORM WITHOUT DATA
    if villageID != None:
        # IF A VILLAGE ID WAS PASSED IN ...

        # GET MEMBER DATA; NAME, # OF CLASSES, NEED CERTIFICATION
        member = db.session.query(Member).filter(Member.Member_ID == villageID).first()
        if member == None:
            memberName = ''
        else:
            memberName = member.First_Name
            if member.Nickname != None and member.Nickname != '':
                memberName += ' (' + member.Nickname + ')'
            memberName += ' ' + member.Last_Name
            lightSpeedID = '123456'

        # CERTIFICATION STATUS
        if member.Certified:
            certificationStatus = 'Certified-RA'
        else:
            certificationStatus = 'Not certified'
            if member.Certification_Training_Date:
                certificationStatus = member.Certification_Training_Date.strftime('%m-%d-%Y')
        
        # DISPLAY THE COURSES TAKEN DATA FOR THAT VILLAGE ID
        
        sp = "EXEC coursesTaken '" + villageID + "'" 
        sql = SQLQuery(sp)
        coursesTaken = db.engine.execute(sql)

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
            
            coursesTakenItem = {
                'enrollmentID':c.Enrollee_Record_ID,
                'term':c.Course_Term,
                'courseNum':c.Course_Number + '-' + c.Section_ID,
                'title':c.Course_Title,
                'dates':sectionDates,
                'times':c.Section_Note,
                'instructor':instructor,
                'receipt':c.Receipt_Number
            }
            coursesTakenDict.append(coursesTakenItem)
    
        # BUILD CURRENT REGISTRATION TABLE, i.e., ENROLLMENTS THIS TERM
        
        sp = "EXEC enrollments '" + villageID + "', '" + term + "'"
        sql = SQLQuery(sp)
        enrolled = db.engine.execute(sql)
        
        enrolledDict = []
        enrolledItem = []
        
        for e in enrolled:
            if e.Instructor_Last_Name == None or e.Instructor_Last_Name == '':
                instructor = ''
            else:
                instructor = e.Instructor_Last_Name + ', ' + e.Instructor_First_Name
                if e.Instructor_NickName != None and e.Instructor_NickName != '':
                    instructor += " (" + e.Instructor_NickName + ")"

            courseFee = e.Course_Fee
            suppliesFee = e.Supplies_Fee
            extPrice = e.Course_Fee + e.Supplies_Fee  

            if (e.Taxable):
                taxable='True'
            else:
                taxable='False' 
           
            enrolledItem = {
                'enrollmentID':e.Enrollee_Record_ID,
                'term':e.Course_Term,
                'courseNum':e.Course_Number + e.Section_ID,
                'title':e.Course_Title,
                'instructor':instructor,
                'courseFee':courseFee,
                'suppliesFee':suppliesFee,
                'extPrice':extPrice,
                'taxable':taxable,
                'receipt':e.Receipt_Number
            }
            enrolledDict.append(enrolledItem)
    else:
        memberName = ''
        lightSpeedID = ''
        coursesTakenDict = []
        enrolledDict = []
    
    enrollmentsThisTerm = len(enrolledDict)
    # END OF ROUTINE TO RETRIEVE COURSES ENROLLED IN BY AN INDIVIDUAL

    # BUILD COURSE OFFERING ARRAY FOR A SPECIFIC TERM
    offeringDict = []
    offeringItems = []

    try:
        sp = "EXEC offerings '" + term + "'"
        sql = SQLQuery(sp)
        offerings = db.engine.execute(sql)
        
    except (SQLAlchemyError, DBAPIError) as e:
        errorMsg = "ERROR retrieving offerings "
        flash(errorMsg,'danger')
        return 'ERROR in offering list build.'
    
    if offerings == None:
        flash('There are no courses offerings for this term.','info')
    else:    
        for offering in offerings:
            # GET CLASS SIZE LIMIT
            capacity = offering.Section_Size
            
            seatsAvailable = capacity - offering.seatsTaken

            if offering.Section_Closed_Date == None: 
                statusClosed = ''
            else:
                if (offering.Section_Closed_Date.date() >= todays_date):
                    statusClosed = ''
                else:
                    statusClosed = 'CLOSED'
            
            seatsAvailable = capacity - offering.seatsTaken
            if (seatsAvailable > 0):
                statusFull = ''
            else:
                statusFull = 'FULL'
            
            fee = offering.courseFee

            if (offering.datesNote == None):
                datesNote = ''
            else:
                datesNote = 'Meets - ' + offering.datesNote

            #   LOOK UP PREREQUISITE FOR COURSE
            prerequisites = db.session.query(Course.Course_Prerequisite).filter(Course.Course_Number == offering.courseNumber).scalar()
            if (prerequisites == None) or prerequisites == '':
                prerequisites = ''          

            offeringItems = {
                'sectionName':offering.courseNumber + '-' + offering.sectionID,
                'term':term,
                'courseNumber':offering.courseNumber,
                'title':offering.title,
                'instructorName':offering.instructorName,
                'dates':offering.Section_Dates,
                'notes':datesNote,
                'capacity':capacity,
                'seatsTaken':offering.seatsTaken,
                'seatsAvailable':seatsAvailable,
                'fee':fee,
                'prereq':prerequisites,
                'supplies':offering.Section_Supplies,
                'suppliesFee':offering.Section_Supplies_Fee,
                'fullMsg':statusFull,
                'closedMsg':statusClosed
            }
            offeringDict.append(offeringItems)

    return render_template("classes.html",memberID=villageID,memberArray=memberArray,\
    todaySTR=todaySTR,termArray=termArray,courseArray=courseArray,memberName=memberName,\
    scheduleDict=coursesTakenDict, offeringDict=offeringDict,term=term,staffID=staffID,\
    staffName=staffName,isDBA=isDBA,isMgr=isMgr,enrolledDict=enrolledDict,\
    certificationStatus=certificationStatus,enrollmentsThisTerm=enrollmentsThisTerm,\
    moreThan2ClassesAllowedDateSTR=moreThan2ClassesAllowedDateSTR,moreThan2ClassesAllowed=moreThan2ClassesAllowed,\
    repeatClassesAllowedDateSTR=repeatClassesAllowedDateSTR,repeatClassesAllowed=repeatClassesAllowed,\
    lightSpeedID=lightSpeedID)

@app.route('/removeEnrollmentRecord')
def removeEnrollmentRecord():
    recordID=request.args.get('recordID')
    enrollment = db.session.query(CourseEnrollee).filter(CourseEnrollee.ID == recordID).first()
    if (enrollment == None):
        return "ERROR - record not found."
    else:
        try:
            db.session.delete(enrollment)
            db.session.commit()
        except:
            return "ERROR - enrollment delete failed."
    return "SUCCESS - enrollment record was removed."

@app.route('/getCourseDescription')
def getCourseDescription():
    courseNumber = request.args.get('courseNumber')
    courseDescription = db.session.query(Course.Course_Description).filter(Course.Course_Number == courseNumber).scalar()
    return jsonify(courseDescription=courseDescription)


@app.route('/getCourseNotes')
def getCourseNotes():
    courseNumber = request.args.get('courseNumber')
    courseNote = db.session.query(Course.Course_Note).filter(Course.Course_Number == courseNumber).scalar()
    return jsonify(courseNote=courseNote)

@app.route('/getCourseMembers')
def getCourseMembers():
    sectionNumber = request.args.get('sectionNumber')[0:6]
    courseNumber, sectionID = sectionNumber.split("-",1)
    term = db.session.query(ControlVariables.Current_Course_Term).filter(ControlVariables.Shop_Number == 1).scalar()

    sql = "SELECT m.First_Name as firstName, m.Last_Name as lastName, m.NickName as nickName, m.Member_ID as memberID"
    sql += " FROM tblCourse_Enrollees e"
    sql += " LEFT JOIN tblMember_Data m ON e.Member_ID = m.Member_ID "
    sql += "WHERE e.Course_Number = '" + courseNumber + "' "
    sql += "AND e.Section_ID = '" + sectionID + "' "
    sql += "AND e.Course_Term = '" + term + "' "
    sql += "ORDER BY m.Last_Name, m.First_Name"

    enrollees = db.session.execute(sql)
    if enrollees:
        memberList = '<ul>'
        for e in enrollees:
            if e.lastName: 
                memberName = e.firstName
                if e.nickName:
                    memberName += ' (' + e.nickName + ')'
                memberName += ' ' + e.lastName + ' [' + e.memberID + ']'
                memberList += '<li>' + memberName + '</li>'
        memberList += '</ul>'
    else:
        memberList = 'No one enrolled.' 

    return jsonify(memberList=memberList)

@app.route('/addEnrollmentRecord')
def addEnrollmentRecord():
    todays_date = date.today()
    todaySTR = todays_date.strftime('%m-%d-%Y')

    term=db.session.query(ControlVariables.Current_Course_Term).filter(ControlVariables.Shop_Number==1).scalar()
    sectionNumber = request.args.get('sectionNumber')
    sectionID = sectionNumber[-1]
    villageID = request.args.get('villageID')
    approval = request.args.get('approval')
    staffID = getStaffID()
    courseNumber, sectionID = sectionNumber.split("-",1)

    # IS THE MEMBER ALREADY ENROLLED IN THIS CLASS?
    enrolled = db.session.query(CourseEnrollee)\
        .filter(CourseEnrollee.Course_Term == term)\
        .filter(CourseEnrollee.Course_Number == courseNumber)\
        .filter(CourseEnrollee.Section_ID == sectionID)\
        .filter(CourseEnrollee.Member_ID == villageID).first()
    if (enrolled):
        errorMsg = "The member is already enrolled in " + sectionNumber + "."
        flash (errorMsg,'info')
        return errorMsg

    sqlInsert = "INSERT INTO tblCourse_Enrollees (Course_Term, Course_Number, "
    sqlInsert += "Section_ID, Member_ID, Receipt_Number, Date_Enrolled, "
    sqlInsert += "Prerequisite_Met_By, Registered_By) "
    sqlInsert += "VALUES ('" + term + "', '" + courseNumber + "', '" + sectionID
    sqlInsert += "', '" + villageID + "', 'PENDING','" + todaySTR 
    sqlInsert += "','" + approval + "','" + staffID + "')"
    # print('.......................................')
    # print(sqlInsert)
    # print('.......................................')
    try:
        db.session.execute(sqlInsert)
        db.session.commit()
        flash('Class added.','success')
        return "Class added."
    except (IntegrityError) as e:
        db.session.rollback()
        errorMsg = 'ERROR - Member already has this class.'
        flash(errorMsg,'info')
        return errorMsg

    except (Exception) as e:
        print('Exception - ',str(e))
        db.session.rollback()
        errorMsg = 'ERROR - cannot add enrollment record.'
        flash(errorMsg,'danger')
        return errorMsg

    
    # newEnrollment = CourseEnrollee(
    #         Course_Term = term,
    #         Course_Number = courseNumber,
    #         Section_ID = sectionID,
    #         Member_ID = villageID,
    #         Receipt_Number = 'PENDING',
    #         Date_Enrolled = todaySTR,
    #         Prerequisite_Met_By = approval,
    #         Registered_By = staffID
    # )
    # try:
    #     db.session.add(newEnrollment)
    #     db.session.commit()
    #     return "SUCCESS"

    # except (IntegrityError) as e:
    #     db.session.rollback()
    #     print('IntegrityError e.orig - ',str(e.orig))
    #     errorMsg = "ERROR - Duplicate course."
    #     flash(errorMsg,'info')
    #     return (errorMsg)

    # except (SQLAlchemyError) as e:
    #     db.session.rollback()
    #     errorMsg = "ERROR adding enrollment record." 
    #     print('SQLAlchemyError e.orig - ',str(e.orig),'e.params - ',str(e.params))
    #     flash(errorMsg,'danger')
    #     return errorMsg

    # except (DBAPIError) as e:
    #     db.session.rollback()
    #     errorMsg = "ERROR adding enrollment record." 
    #     print('DBAPIError e.orig - ',str(e.orig),'e.params - ',str(e.params))
    #     flash(errorMsg,'danger')
    #     return errorMsg

    # except (Exception) as e:
    #     print('Exception e.orig - ',str(e.orig))
    #     db.session.rollback()
    #     errorMsg = 'ERROR adding enrollment record.'
    #     flash(errorMsg,'danger')
    #     return errorMsg


@app.route("/updateReceiptNumber")
def updateReceiptNumber():
    memberID = request.args.get('memberID')
    receiptNumber = request.args.get('receiptNumber')

    # RAW SQL APPROACH
    try:
        sqlUpdate = "UPDATE tblCourse_Enrollees set Receipt_Number = '"
        sqlUpdate += receiptNumber + "' where Member_ID = '" + memberID + "' and Receipt_Number = 'PENDING'"
        db.engine.execute(sqlUpdate)
        msg = "Classes are now marked Paid."
    except (SQLAlchemyError, DBAPIError) as e:
        msg = "ERROR updating pending records."
       
    return jsonify(msg=msg)

def logChange(colName,memberID,newData,origData):
    if staffID == None:
        staffID = '111111'
    if staffID == '':
        staffID = '111111'

    # Write data changes to tblMember_Data_Transactions
    est = timezone('America/New_York')
    transactionDate = datetime.now(est)
    newTransaction = MemberTransactions(
        Transaction_Date = transactionDate,
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

def getStaffID():
    if 'staffID' in session:
        staffID = session['staffID']
    else:
        staffID = '604875'
    return staffID

def getShopID():
    if 'shopID' in session:
        shopID = session['shopID']
    else:
        # SET RA FOR TESTING; SEND FLASH ERROR MESSAGE FOR PRODUCTION
        shopID = 'RA'
        msg = "Missing location information; Rolling Acres assumed."
        #flash(msg,"danger")
    if shopID =='RA':
        shopNumber = 1
    else:
        if shopID == 'BW':
            shopNumber = 2
        else:
            msg = "The shopID of " + shopID + "is invalid, 'RA' assumed"
            #flash (msg,'danger')
            shopID == 'RA'
            shopNumber = 1
    return shopID    


@app.route("/prtMemberSchedule/<string:memberID>/",methods=["GET","POST"])
def prtMemberSchedule(memberID):
    est = timezone('America/New_York')
    todays_date = date.today()
    todaySTR = todays_date.strftime('%m-%d-%Y')
    term = db.session.query(ControlVariables.Current_Course_Term).filter(ControlVariables.Shop_Number == 1).scalar()
    location = 'Rolling Acres'

    # EXECUTE STORED PROCEDURE
    sp = "EXEC memberClassSchedule '" + memberID + "', '" + term + "'"
    sql = SQLQuery(sp)
    classSchedule = db.engine.execute(sql)
    
    # BUILD MEMBER SCHEDULE ARRAY FOR CURRENT TERM
    scheduleDict = []
    scheduleItems = []
    for c in classSchedule:
        memberName = c.Student_First_Name + ' ' + c.Student_Last_Name
        if (c.Instructor_Last_Name == None or c.Instructor_Last_Name == ''):
            instructorName = ''
        else:
            if (c.Instructor_First_Name != ''):
                instructorName = c.Instructor_First_Name + ' ' + c.Instructor_Last_Name
            else:
                instructorName = c.Instructor_Last_Name

        scheduleItems = {
                'sectionNumber':c.Course_Number + '-' + c.Section_ID,
                'courseNumber':c.Course_Number,
                'courseTitle':c.Course_Title,
                'instructorName':instructorName,
                'courseDates':c.Section_Dates,
                'courseTimes':c.Section_Notes,
                'courseLocation':location
            }
        scheduleDict.append(scheduleItems)

    return render_template('rptMemberClassSchedule.html',\
    scheduleDict=scheduleDict,memberName=memberName,todaySTR=todaySTR,term=term)


@app.route("/prtEnrollmentReceipt/<string:memberID>/",methods=["GET","POST"])
def prtEnrollmentReceipt(memberID):
    todays_date = date.today()
    todaySTR = todays_date.strftime('%m-%d-%Y')
    term = db.session.query(ControlVariables.Current_Course_Term).filter(ControlVariables.Shop_Number == 1).scalar()
    location = 'Rolling Acres'

    # EXECUTE STORED PROCEDURE
    #sp = "EXEC memberClassSchedule '" + memberID + "', '" + term + "'"
    sp = "EXEC enrollmentReceipt " + memberID 
    sql = SQLQuery(sp)
    classSchedule = db.engine.execute(sql)
    
    # BUILD MEMBER SCHEDULE ARRAY FOR CURRENT TERM
    scheduleDict = []
    scheduleItems = []
    for c in classSchedule:
        memberName = c.Student_First_Name + ' ' + c.Student_Last_Name
        if (c.Instructor_Last_Name == None or c.Instructor_Last_Name == ''):
            instructorName = ''
        else:
            if (c.Instructor_First_Name != ''):
                instructorName = c.Instructor_First_Name + ' ' + c.Instructor_Last_Name
            else:
                instructorName = c.Instructor_Last_Name

        scheduleItems = {
                'sectionNumber':c.Course_Number + '-' + c.Section_ID,
                'courseNumber':c.Course_Number,
                'courseTitle':c.Course_Title,
                'instructorName':instructorName,
                'courseDates':c.Section_Dates,
                'courseTimes':c.Section_Notes,
                'courseLocation':location
            }
        scheduleDict.append(scheduleItems)

    return render_template('rptEnrollmentReceipt.html',\
    scheduleDict=scheduleDict,memberName=memberName,todaySTR=todaySTR)