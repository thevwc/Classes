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

@app.route('/', defaults={'staffID':None,'villageID':None,'term':None})
@app.route('/index/', defaults={'staffID':None,'villageID':None,'term':None})
@app.route('/index//<villageID>/',defaults={'staffID':None,'term':None})
@app.route('/index/<staffID>/<villageID>/',defaults={'term':None})
@app.route("/classes",defaults={'staffID':None,'villageID':None,'term':None})
@app.route("/classes/<staffID>/",defaults={'villageID':None,'term':None})
@app.route("/classes//<villageID>/",defaults={'staffID':None,'term':None})
@app.route("/classes//<villageID>/<term>",defaults={'staffID':None})
@app.route("/classes/<staffID>/<villageID>/",defaults={'term':None})
@app.route("/classes/<staffID>/<villageID>/<term>")
def index(staffID,villageID,term):
    # GET TODAY'S DATE
    todays_date = date.today()
    todaySTR = todays_date.strftime('%m-%d-%Y')

    #print('staffID - ',staffID,'\nvillageID - ',villageID, '\nterm - ',term)
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
    repeatClassesAllowedDate = controlVariables.Repeat_Classes_Allowed_Date
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
    if villageID != None:
        
        # IF A VILLAGE ID WAS PASSED IN ...

        # GET MEMBER DATA; NAME, # OF CLASSES, NEED CERTIFICATION
        member = db.session.query(Member).filter(Member.Member_ID == villageID).first()
        #print('Name - ',member.Last_Name)
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

        # GET NUMBER OF CLASSES MEMBER IS CURRENTLY ENROLLED
        enrollmentsThisTerm = db.session.query(func.count(CourseEnrollee.Member_ID))\
            .filter(CourseEnrollee.Member_ID == villageID)\
            .filter(CourseEnrollee.Course_Term == term)\
            .scalar()
        
        # DISPLAY THE COURSES TAKEN DATA FOR THAT VILLAGE ID
        # SQL APPROACH
        sql = "SELECT tblCourse_Enrollees.ID AS Enrollee_Record_ID, tblCourse_Enrollees.Course_Term AS Course_Term, "
        sql += "tblCourse_Enrollees.Course_Number AS Course_Number, tblCourse_Enrollees.Date_Enrolled as DateEnrolled, "
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
        sql += "AND tblCourse_Enrollees.Course_Term <> '" + term + "' "
        sql += "ORDER BY tblCourse_Enrollees.Course_Number, tblCourse_Enrollees.Section_ID, Course_Term desc "
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
            
            coursesTakenItem = {
                'enrollmentID':c.Enrollee_Record_ID,
                'term':c.Course_Term,
                'courseNum':c.Course_Number,
                'title':c.Course_Title,
                'dates':sectionDates,
                'times':c.Section_Note,
                'instructor':instructor
            }
            coursesTakenDict.append(coursesTakenItem)

        # BUILD CURRENT REGISTRATION TABLE
        sql = "SELECT tblCourse_Enrollees.ID AS Enrollee_Record_ID, tblCourse_Enrollees.Course_Term AS Course_Term, "
        sql += "tblCourse_Enrollees.Course_Number AS Course_Number, tblCourse_Enrollees.Date_Enrolled as DateEnrolled, "
        sql += "tblCourse_Enrollees.Section_ID, tblCourse_Enrollees.Supply_Sets, tblCourses.Course_Title AS Course_Title, "
        sql += "tblCourses.Course_Fee as Course_Fee, tblCourses.Course_Supplies_Are_Taxable as Taxable, "
        sql += "tblCourse_Enrollees.Member_ID AS Student_ID, tblMember_Data.Last_Name AS Student_Last_Name, "
        sql += "tblMember_Data.First_Name AS Student_First_Name, tblMember_Data.NickName as Student_NickName, "
        sql += "tblCourse_Offerings.Section_Dates as Section_Dates, tblCourse_Offerings.Section_Dates_Note as Section_Note, "
        sql += "tblMember_Data_1.Last_Name AS Instructor_Last_Name, "
        sql += "tblMember_Data_1.First_Name AS Instructor_First_Name, tblMember_Data_1.NickName AS Instructor_NickName, "
        sql += "tblCourse_Enrollees.Date_Enrolled AS Date_Enrolled, tblCourse_Enrollees.Receipt_Number AS Receipt_Number, "
        sql += "tblCourse_Offerings.Section_ID AS Section_ID, tblCourse_Offerings.Section_Dates_Note AS Section_Notes, "
        sql += "tblCourse_Offerings.Section_Supplies_Fee as Supplies_Fee "
        sql += "FROM tblCourses INNER JOIN (((tblCourse_Enrollees INNER JOIN tblCourse_Offerings "
        sql += "ON (tblCourse_Offerings.Course_Number = tblCourse_Enrollees.Course_Number) "
        sql += "AND (tblCourse_Offerings.Course_Term = tblCourse_Enrollees.Course_Term) "
        sql += "AND (tblCourse_Enrollees.Section_ID = tblCourse_Offerings.Section_ID)) "
        sql += "LEFT JOIN tblMember_Data ON tblCourse_Enrollees.Member_ID = tblMember_Data.Member_ID) "
        sql += "LEFT JOIN tblMember_Data AS tblMember_Data_1 ON tblCourse_Offerings.Instructor_ID = tblMember_Data_1.Member_ID) "
        sql += "ON tblCourses.Course_Number = tblCourse_Offerings.Course_Number "
        sql += "WHERE tblCourse_Enrollees.Member_ID = '" + villageID + "' "
        sql += "AND tblCourse_Enrollees.Course_Term = '" + term + "' "
        sql += "ORDER BY tblCourse_Enrollees.Course_Number, tblCourse_Enrollees.Section_ID "
        enrolled = db.session.execute(sql)
        
        enrolledDict = []
        enrolledItem = []

        for e in enrolled:
            if e.Instructor_Last_Name == None or e.Instructor_Last_Name == '':
                instructor = ''
            else:
                instructor = e.Instructor_Last_Name + ', ' + e.Instructor_First_Name
                if e.Instructor_NickName != None and e.Instructor_NickName != '':
                    instructor += " (" + e.Instructor_NickName + ")"
            #feeValue = decimal.Decimal(offering.courseFee)
            #fee = f"{feeValue:5.2}"

            courseFee = e.Course_Fee
            suppliesFee = e.Supplies_Fee
            extPrice = e.Course_Fee + e.Supplies_Fee  

            if (e.Taxable):
                taxable='True'
            else:
                taxable='False' 
            # if e.Section_Dates == None:
            #     sectionDates = ''
            # else:
            #     sectionDates = e.Section_Dates
            #print(e.DateEnrolled.date,type(e.DateEnrolled))
            #print(todays_date,type(todays_date))
            #dateEnrolled = e.DateEnrolled.strftime('%m-%d-%Y')
            
            #print(e.Course_Term, e.Course_Number, e.Course_Title, sectionDates, e.Section_Note, instructor, e.Receipt_Number)

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
            #print(enrolledItem)


    else:
        memberName = ''
        lightSpeedID = ''
        coursesTakenDict = []
        enrolledDict = []
    # END OF ROUTINE TO RETRIEVE COURSES ENROLLED IN BY AN INDIVIDUAL

    # BUILD COURSE OFFERING ARRAY FOR A SPECIFIC TERM
    offeringDict = []
    offeringItems = []

    # SQL STATEMENTS approach
    sqlOfferings = "SELECT top 20 o.ID as ID, o.Course_Term as term, "
    sqlOfferings += "o.Course_Number as courseNumber,o.Section_ID as sectionID, "
    sqlOfferings += "o.Section_Dates, o.Section_Dates_Note as datesNote, o.Section_Size, "
    sqlOfferings += "o.Section_Supplies, o.Section_Supplies_Fee, "
    sqlOfferings += "o.Section_Closed_Date, o.Section_Start_Date, "
    sqlOfferings += "c.Course_Title as title, c.Course_Fee as courseFee, "
    sqlOfferings += "c.Course_Prerequisite as prereq, "
    sqlOfferings += "m.First_Name + ' ' + m.Last_Name as instructorName "
    sqlOfferings += "FROM tblCourse_Offerings o "
    sqlOfferings += "LEFT JOIN tblCourses c ON c.Course_Number = o.Course_Number "
    sqlOfferings += "LEFT JOIN tblMember_Data m ON m.Member_ID = o.Instructor_ID "
    sqlOfferings += "WHERE o.Course_Term = '" + term + "' "
    sqlOfferings += "ORDER BY o.Course_Number, o.Section_ID"

    try:
        offerings = db.engine.execute(sqlOfferings)
    except (SQLAlchemyError, DBAPIError) as e:
        #print('ERROR - ',e)
        errorMsg = "ERROR retrieving offerings "
        flash(errorMsg,'danger')
        return 'ERROR in offering list build.'

    if offerings == None:
        flash('There are no courses offerings for this term.','info')
    else: 
        #print('there are some offerings ...')   
        for offering in offerings:
            # GET CLASS SIZE LIMIT
            capacity = offering.Section_Size

            # GET COUNT OF SEATS TAKEN
            seatsTaken = db.session.query(func.count(CourseEnrollee.Member_ID))\
                .filter(CourseEnrollee.Course_Term == term)\
                .filter(CourseEnrollee.Course_Number == offering.courseNumber)\
                .filter(CourseEnrollee.Section_ID == offering.sectionID)\
                .scalar()
            
            seatsAvailable = capacity - seatsTaken
            if (offering.Section_Closed_Date):
                statusClosed = 'CLOSED'
            else:
                statusClosed = ''

            seatsAvailable = capacity - seatsTaken
            if (seatsAvailable > 0):
                statusFull = ''
            else:
                statusFull = 'FULL'

            fee = offering.courseFee
            #feeValue = decimal.Decimal(offering.courseFee)
            #fee = f"{feeValue:5.2}"

            if (offering.datesNote == None):
                datesNote = ''
            else:
                datesNote = 'Meets - ' + offering.datesNote

            if (offering.prereq == None):
                prereq = ''
            else:
                prereq = offering.prereq


            offeringItems = {
                'sectionName':offering.courseNumber + '-' + offering.sectionID,
                'term':term,
                'courseNumber':offering.courseNumber,
                'title':offering.title,
                'instructorName':offering.instructorName,
                'dates':offering.Section_Dates,
                'notes':datesNote,
                'capacity':capacity,
                'seatsTaken':seatsTaken,
                'seatsAvailable':seatsAvailable,
                'fee':fee,
                'prereq':prereq,
                'supplies':offering.Section_Supplies,
                'suppliesFee':offering.Section_Supplies_Fee,
                'fullMsg':statusFull,
                'closedMsg':statusClosed
            }
            offeringDict.append(offeringItems)

    #  BUILD DICT OF CURRENT REGISTRATIONS


    #print('villageID - ',villageID)
    #print('term - ',term.upper())
    return render_template("classes.html",memberID=villageID,memberArray=memberArray,\
    todaySTR=todaySTR,termArray=termArray,courseArray=courseArray,memberName=memberName,\
    scheduleDict=coursesTakenDict, offeringDict=offeringDict,term=term.upper(),staffID=staffID,\
    staffName=staffName,isDBA=isDBA,isMgr=isMgr,enrolledDict=enrolledDict,\
    certificationStatus=certificationStatus,enrollmentsThisTerm=enrollmentsThisTerm,\
    moreThan2ClassesAllowedDateSTR=moreThan2ClassesAllowedDateSTR,moreThan2ClassesAllowed=moreThan2ClassesAllowed,\
    lightSpeedID=lightSpeedID)


    


# Finally solved my problem with the following function :

def execute_stored_procedure(engine, procedure_name):
    res = {}
    connection = engine.raw_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("EXEC "+procedure_name)
        cursor.close()
        connection.commit()
        res['status'] = 'OK'
    except Exception as e:
        res['status'] = 'ERROR'
        res['error'] = e
    finally:
        connection.close() 
    return res

@app.route('/removeEnrollmentRecord')
def removeEnrollmentRecord():
    recordID=request.args.get('recordID')
    #print('record to delete - ',recordID)
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
    sectionNumber = request.args.get('sectionNumber')
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
    #print('addEnrollmentRecord')
    sectionNumber = request.args.get('sectionNumber')
    villageID = request.args.get('villageID')
    staffID = request.args.get('staffID')
    #print('staffID - ',staffID)
    #print('sectionNumber - ',sectionNumber)
    courseNumber, sectionID = sectionNumber.split("-",1)
    #print('courseNumber - ',courseNumber)
    #print('sectionID - ',sectionID)

    newEnrollment = CourseEnrollee(
            Course_Term = term,
            Course_Number = courseNumber,
            Section_ID = sectionID,
            Member_ID = villageID,
            Receipt_Number = 'PENDNG',
            Date_Enrolled = todays_date,
            Registered_By = staffID
    )
    try:
        db.session.add(newEnrollment)
        db.session.commit()
        return "SUCCESS"

    except (IntegrityError) as e:
        #print('..........IngegrityError -',e)
        db.session.rollback()
        errorMsg = "ERROR - Duplicate course."
        return (errorMsg)

    except (SQLAlchemyError, DBAPIError) as e:
        db.session.rollback()
        #print('..........ERROR - ',e)
        errorMsg = "ERROR adding enrollment record. "
        flash(errorMsg,'danger')
        return errorMsg

@app.route("/updateReceiptNumber")
def updateReceiptNumber():
    memberID = request.args.get('memberID')
    receiptNumber = request.args.get('receiptNumber')
    print('memberID - ',memberID)
    print('receiptNumber - ',receiptNumber)
    print('updateReceiptNumber rtn')

    # SQLALCHEMY APPROACH
    # try:
    #     db.session.query(CourseEnrollee)\
    #         .filter(CourseEnrollee.Member_ID == memberID)\
    #         .filter(CourseEnrollee.Receipt_Number == 'PENDNG')\
    #         .update({CourseEnrollee.Receipt_Number:receiptNumber})
    # except (SQLAlchemyError, DBAPIError) as e:
    #      print('ERROR - ',e)
    #      msg = "ERROR updating pending records."
    #      return jsonify(msg=msg)
    
    # msg="SUCCESS updating pending records."
    # return jsonify(msg=msg)

    # RAW SQL APPROACH
    sqlUpdate = "UPDATE tblCourse_Enrollees SET Receipt_Number = '" + receiptNumber + "' "
    sqlUpdate += "WHERE Member_ID = '" + memberID + "' AND Receipt_Number = 'PENDNG'"
    
    print('...................................')
    print(sqlUpdate)
    print('...................................')
    try:
        db.session.execute(sqlUpdate)
    except (SQLAlchemyError, DBAPIError) as e:
        print('ERROR - ',e)
        msg = "ERROR updating pending records."
        return jsonify(msg=msg)

    msg = "SUCCESS in updating pending records."
    
    return jsonify(msg=msg)