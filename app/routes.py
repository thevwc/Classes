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

@app.route('/', defaults={'villageID':None,'term':None})
@app.route('/index/', defaults={'villageID':None,'term':None})
@app.route('/index/<villageID>/')
@app.route("/classes",defaults={'villageID':None,'term':None})
@app.route("/classes/<villageID>",defaults={'term':None})
@app.route("/classes/<villageID>/<term>")
def index(villageID,term):
    #print('1. villageID - ',villageID, '\nterm - ',term)
    if (term == None):
        term = db.session.query(ControlVariables.Current_Course_Term).filter(ControlVariables.Shop_Number == 1).scalar()
    #print('2. villageID - ',villageID, '\nterm - ',term)

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
    if villageID != None:
        #  return render_template("classes.html",memberID="",memberArray=memberArray,\
        #  termArray=termArray,courseArray=courseArray)
    
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
    else:
        memberName = ''
        coursesTakenDict = []
    # END OF ROUTINE TO RETRIEVE COURSES TAKEN BY AN INDIVIDUAL

    # BUILD COURSE OFFERING ARRAY FOR A SPECIFIC TERM
    #print('begin build course offering ...')
    if (term != None):
        offeringDict = []
        offeringItems = []

        # SQL STATEMENTS approach
        sqlOfferings = "SELECT o.Course_Term as term,o.Course_Number as courseNumber,o.Section_ID as sectionID, "
        sqlOfferings += "o.Section_Dates, o.Section_Dates_Note, o.Section_Size, "
        sqlOfferings += "o.Prerequisite_Course, "
        sqlOfferings += "o.Section_Supplies, o.Section_Supplies_Fee, "
        sqlOfferings += "o.Section_Closed_Date, o.Section_Start_Date, "
        sqlOfferings += "c.Course_Title as title, c.Course_Fee as courseFee, "
        sqlOfferings += "m.First_Name + ' ' + m.Last_Name as instructorName "
        sqlOfferings += "FROM tblCourse_Offerings o "
        sqlOfferings += "LEFT JOIN tblCourses c ON c.Course_Number = o.Course_Number "
        sqlOfferings += "LEFT JOIN tblMember_Data m ON m.Member_ID = o.Instructor_ID "
        sqlOfferings += "WHERE o.Course_Term = '" + term + "' "
        sqlOfferings += "ORDER BY o.Course_Number, o.Section_ID"
        
        #print(sqlOfferings)

        try:
            offerings = db.engine.execute(sqlOfferings)
        except (SQLAlchemyError, DBAPIError) as e:
            print('ERROR - ',e)
            errorMsg = "ERROR retrieving offerings "
            flash(errorMsg,'danger')
            return 'ERROR in offering list build.'

        #for o in offerings:
        #    print (o.term, o.courseNumber, o.title, o.instructor)

        # END OF SQL STATEMENTS approach 


        # SQLAlchemy approach ...
        # offerings = db.session.query(CourseOffering)\
        #     .filter(CourseOffering.Course_Term == term)\
        #     .order_by(CourseOffering.Course_Number, CourseOffering.Section_ID)\
        #     .limit(10)
        if offerings == None:
            flash('There are no courses offerings for this term.','info')
        else: 
            #print('there are some offerings ...')   
            for offering in offerings:
                
        #         # GET COURSE TITLE
        #         courseRecord = db.session.query(Course).filter(Course.Course_Number == offering.Course_Number).first()
        #         courseTitle = courseRecord.Course_Title
        #         courseFee = courseRecord.Course_Fee

        #         # GET INSTRUCTOR NAME
        #         instructor = db.session.query(Member).filter(Member.Member_ID == offering.Instructor_ID).first()
        #         if (instructor):
        #             instructorName = instructor.First_Name + ' ' + instructor.Last_Name
        #         else:
        #             instructorName = ''
        # END OF SQLAlchemy approach

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

                offeringItems = {
                    'sectionName':offering.courseNumber + '-' + offering.sectionID,
                    'term':term,
                    'courseNumber':offering.courseNumber,
                    'title':offering.title,
                    'instructorName':offering.instructorName,
                    'dates':offering.Section_Dates,
                    'notes':offering.Section_Dates_Note,
                    'capacity':capacity,
                    'seatsTaken':seatsTaken,
                    'seatsAvailable':seatsAvailable,
                    'fee':offering.courseFee,
                    'supplies':offering.Section_Supplies,
                    'suppliesFee':offering.Section_Supplies_Fee,
                    'fullMsg':statusFull,
                    'closedMsg':statusClosed
                }
                offeringDict.append(offeringItems)
            

    #print('term sent to browser - ',term)
    return render_template("classes.html",memberID=villageID,memberArray=memberArray,\
    todaySTR=todaySTR,termArray=termArray,courseArray=courseArray,memberName=memberName,\
    scheduleDict=coursesTakenDict, offeringDict=offeringDict,term=term)


    


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

