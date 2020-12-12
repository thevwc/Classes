# routes.py
from flask import session, render_template, flash, redirect, url_for, request, jsonify, json, make_response, after_this_request
from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap
from werkzeug.urls import url_parse
from app.models import ShopName, Member, Course,CourseOffering,CourseEnrollee,\
ControlVariables, MemberTransactions

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
        if n.Nickname != None:
            name += ' (' + n.Nickname + ')'
        name += ' [' + n.Member_ID + ']'
        
        memberArray.append(name)
        
    # BUILD COURSE LIST
    courseArray = []
    courses = db.session.query(Course).order_by(Course.Course_Number).all()
    if courses == None:
        flash('There are no courses to list.','danger')
        return render_template("classes.html",memberID="",memberArray=memberArray,courseArray='')
    
    for c in courses:
        #print(c.Course_Number,c.Course_Title)
        courseLine = c.Course_Number + ' - ' + c.Course_Title
        print(courseLine)
        courseArray.append(courseLine)

    # IF A VILLAGE ID WAS NOT PASSED IN, DISPLAY THE classes.html FORM WITHOUT DATA
    if villageID == None:
         return render_template("classes.html",memberID="",memberArray=memberArray,courseArray=courseArray)
    
    # IF A VILLAGE ID WAS PASSED IN ...
    # DISPLAY THE CORRESPONDING MEMBER DATA FOR THAT VILLAGE ID
    # applicant = db.session.query(classes).filter(classes.MemberID == villageID).first()
    
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
    todaySTR=todaySTR,courseArray=courseArray)


@app.route("/updateclasses", methods=('GET','POST'))
def updateclasses():
    # POST REQUEST; PROCESS WAIT LIST APPLICATION, ADD TO MEMBER_DATA, INSERT TRANSACTION ('ADD')
    memberID = request.form.get('memberID')
    if request.form.get('classes') == 'CANCEL':
        return redirect(url_for('classes',villageID=memberID))

   # RETRIEVE FORM VALUES
    expireDate = request.form.get('expireDate')
    firstName = request.form.get('firstName')
    lastName = request.form.get('lastName')
    street = request.form.get('street')
    city = request.form.get('city')
    state = request.form.get('state')
    zip = request.form.get('zip')
    cellPhone = request.form.get('cellPhone')
    homePhone = request.form.get('homePhone')
    eMail = request.form.get('eMail')
    if request.form.get('jan') == 'True':
        jan = True
    else:
        jan = False

    if request.form.get('feb') == 'True':
        feb = True
    else:
        feb = False

    if request.form.get('mar') == 'True':
        mar = True
    else:
        mar = False

    if request.form.get('apr') == 'True':
        apr = True
    else:
        apr = False

    if request.form.get('may') == 'True':
        may = True
    else:
        may = False

    if request.form.get('jun') == 'True':
        jun = True
    else:
        jun = False
    
    if request.form.get('jul') == 'True':
        jul = True
    else:
        jul = False

    if request.form.get('aug') == 'True':
        aug = True
    else:
        aug = False

    if request.form.get('sep') == 'True':
        sep = True
    else:
        sep = False

    if request.form.get('oct') == 'True':
        oct = True
    else:
        oct = False

    if request.form.get('nov') == 'True':
        nov = True
    else:
        nov = False

    if request.form.get('dec') == 'True':
        dec = True
    else:
        dec = False
    
    notes = request.form.get('notes')
    approvedToJoin = request.form.get('approvedToJoin')
    notified = request.form.get('notified')
    applicantAccepts = request.form.get('applicantAccepts')
    applicantDeclines = request.form.get('applicantDeclines')
    noLongerInterested = request.form.get('noLongerInterested')
    plannedCertificationDate = request.form.get('plannedCertificationDate')
    staffID = request.form.get('staffID')

    # GET ID OF STAFF MEMBER 
    staffID = '123456'
    # GET CURRENT DATE AND TIME
    todays_date = datetime.today()
    todaySTR = todays_date.strftime('%m-%d-%Y')

    # IS THIS PERSON ALREADY ON THE classes?
    classesRecord = db.session.query(classes).filter(classes.MemberID == memberID).first()
    if (classesRecord == None):
        # ADD NEW RECORD TO tblMembershipWaitingList
        if plannedCertificationDate == '':
            plannedCertificationDate = None
        
        try:
            newclassesRecord = classes( 
                MemberID = memberID,
                VillageIDexpirationDate = expireDate,
                FirstName = firstName,
                LastName = lastName, 
                StreetAddress = street,
                City = city,
                State = state,
                Zipcode = zip,
                CellPhone = cellPhone,
                HomePhone = homePhone,
                Email = eMail,
                Notes = notes,
                PlannedCertificationDate = plannedCertificationDate,
                AddedByStaffMemberID = staffID,
                Jan = jan,
                Feb = feb,
                Mar = mar,
                Apr = apr,
                May = may,
                Jun = jun,
                Jul = jul,
                Aug = aug,
                Sep = sep,
                Oct = oct,
                Nov = nov,
                Dec = dec,
                DateTimeEntered = todaySTR
            ) 
        
            db.session.add(newclassesRecord)
            db.session.commit()

        except SQLAlchemyError as e:
            error = str(e.__dict__['orig'])
            flash('ERROR - Record not added.'+error,'danger')
            db.session.rollback()
        
        return redirect(url_for('classes'))
    
    # PROCESS UPDATE OF EXISTING WAIT LIST RECORD
    if classesRecord.FirstName != firstName :
        classesRecord.FirstName = firstName
    if classesRecord.LastName != lastName :
        classesRecord.LastName = lastName
    if classesRecord.HomePhone != homePhone :
        classesRecord.HomePhone = homePhone
    if classesRecord.CellPhone != cellPhone :
        classesRecord.CellPhone = cellPhone
       
    if classesRecord.StreetAddress != street :
        classesRecord.StreetAddress = street
    
    if classesRecord.City != city :
        classesRecord.City = city
    if classesRecord.State != state :
        classesRecord.State = state
    if classesRecord.Zipcode != zip :
        classesRecord.Zipcode = zip
    if classesRecord.Email != eMail :
        classesRecord.Email = eMail

    if classesRecord.Notes != notes :
        classesRecord.Notes = notes
    
    if classesRecord.ApprovedToJoin != approvedToJoin :
        classesRecord.ApprovedToJoin = approvedToJoin
    if classesRecord.Notified != notified :
        classesRecord.Notified = notified
    
    


    if classesRecord.Jan != jan:
        classesRecord.Jan = jan
    if classesRecord.Feb != feb :
        classesRecord.Feb = feb
    if classesRecord.Mar != mar:
        classesRecord.Mar = mar
    if classesRecord.Apr != apr:
        classesRecord.Apr = apr
    if classesRecord.May != may:
        classesRecord.May = may
    if classesRecord.Jun != jun:
        classesRecord.Jun = jun
    if classesRecord.Jul != jul:
        classesRecord.Jul = jul
    if classesRecord.Aug != aug:
        classesRecord.Aug = aug
    if classesRecord.Sep != sep:
        classesRecord.Sep = sep
    if classesRecord.Oct != oct:
        classesRecord.Oct = oct
    if classesRecord.Nov != nov:
        classesRecord.Nov = nov
    if classesRecord.Dec != dec:
        classesRecord.Dec = dec
    
    if classesRecord.ApplicantAccepts != applicantAccepts :
        classesRecord.ApplicantAccepts = applicantAccepts
    if classesRecord.ApplicantDeclines != applicantDeclines :
        classesRecord.ApplicantDeclines = applicantDeclines
    if classesRecord.NoLongerInterested != noLongerInterested :
        classesRecord.NoLongerInterested = noLongerInterested
    if classesRecord.PlannedCertificationDate != plannedCertificationDate :
        classesRecord.PlannedCertificationDate = plannedCertificationDate
    
    try:
        db.session.commit()
        flash("Changes to wait list successful","success")
    except Exception as e:
        flash("Could not update Wait List data.","danger")
        db.session.rollback()

    
    return redirect(url_for('classes',villageID=memberID,todaysDate=todaySTR))

@app.route("/printConfirmation/<memberID>")
def printConfirmation(memberID):
    # GET MEMBER NAME
    applicant = db.session.query(classes).filter(classes.MemberID == memberID).first()
    if applicant == None:
        flash ("Error in printing confirmation letter.",'danger')
        return

    displayName = applicant.FirstName + ' ' + applicant.LastName
    todays_date = date.today()
    todays_dateSTR = todays_date.strftime('%m-%d-%Y')
    applicationDate = applicant.DateTimeEntered.strftime('%A, %B %-d, %Y')
    # Using include statement in html file for included text 'classesConfirmation.html' in Template folder
    return render_template("rptAppConfirm.html",displayName=displayName,applicant=applicant,
    applicationDate=applicationDate,todays_date=todays_dateSTR)