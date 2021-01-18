//GET STAFF ID
// IS THERE A STAFF ID ON THE PAGE?
staffID = document.getElementById('staffID').value
if (staffID == 'None' | staffID == null | staffID == '') {
    // IS THERE A STAFF ID STORED IN LOCALSTORAGE?
    staffID = localStorage.getItem('staffID')
    if (!staffID) {
        // PROMPT FOR A STAFF ID
        staffID = prompt("Staff ID - ")
        localStorage.setItem('staffID',staffID)
    }
}

// GET isDBA
const isDBA = document.getElementById('isDBA').value
// GET isMgr
const isMgr = document.getElementById('isMgr').value
// CHECK FOR EITHER isDBA or isMgr
if (isDBA !='True' && isMgr != 'True') {
    // SET MGR OPTIONS
    for (let el of document.querySelectorAll('.dropClassTakenBtn')) el.style.visibility = 'hidden';
}

// GET TERM FROM PAGE
term = document.getElementById('termID').innerHTML

// SHOW ENROLL BUTTONS IF MEMBER HAS BEEN SELECTED
memberID = document.getElementById('memberID').value
if (memberID != 'None' & memberID != ''){
    $(".enrollBtn").filter(function() {
        $(this).toggle()
    })
    // SHOW LIGHTSPEED SECTION
    document.getElementById('lightSpeedFormID').style.display="block";
}

// SHOW ALL CLASSES

// SET selectedCourse TO BLANK
selectedCourse = ''

// DEFINE EVENT LISTENERS
document.getElementById("selectMemberID").addEventListener("change",memberSelectedRtn)
document.getElementById("selectMemberID").addEventListener("click",memberSelectedRtn)
document.getElementById('courseOfferingsTable').addEventListener('click',offeringClickRtn)
document.getElementById('lightspeedBtn').addEventListener('click',updateReceiptNumber)
document.getElementById('lackPrerequisitesID').addEventListener('click',notApprovedRtn)
document.getElementById('metPrerequisitesID').addEventListener('click',approvedRtn)

$(".enrollBtn").click(function() {
    sectionNumber = this.id
    checkForPrerequisites(this.id)
})

$("#selectCourseID").on("change", function() {
    courseData = this.value
    selectedCourse = courseData.slice(0,4)
    $("#courseOfferingsTable tr").filter(function() {
        $(this).toggle($(this).text().indexOf(selectedCourse) > -1)
    })
 });
 
 $('.approvalOptions input[type=radio]').click(function(){
    optionChoice = this.value
    document.getElementById('metPrerequisitesID').removeAttribute('disabled')
    document.getElementById('lackPrerequisitesID').setAttribute('disabled',true) 
})

// FUNCTIONS 
function memberSelectedRtn() {
    memberData = this.value
    localStorage.setItem('memberSelected',this.value) 
    lastEight = memberData.slice(-8)
    selectedMember= lastEight.slice(1,7)

    // GET MEMBER NAME AND COURSES TAKEN 
    link = '/classes/' + selectedMember
    window.location.href = link

}

function showOpenOnly() {
    $(".FULL, .CLOSED").filter(function() {
        $(this).toggle()
    })
}

function showAllClasses() {
     $("#courseOfferingsTable tr").filter(function() {
        $(this).toggle()
     })
 }    

 function checkForPrerequisites(sectionNumber) {
    console.log('checkForPrerequisites rtn')
    btn = document.getElementById(sectionNumber)
    btnTD = btn.parentElement
    parentTR = btnTD.parentElement
    
    // GET ALL VALUES IN ROW
    tds = parentTR.getElementsByTagName("td");
    courseNumber = sectionNumber.slice(0,4)
    courseTitle = tds[1].innerHTML
    document.getElementById('modalCoursePrereqTitle').innerHTML = "Prerequistites for " + courseNumber + " (" + courseTitle + ")"
    document.getElementById('modalSectionNumber').value = sectionNumber 
    
    // CHECK FOR PREREQUISITES
    prereqID = 'p' + sectionNumber
    prereq = document.getElementById(prereqID)
    if (prereq != null) {
        prereqValue = prereq.innerHTML
        if (prereqValue != '') {
            document.getElementById('prerequisites').innerHTML = prereqValue
            $('#coursePrereqModalID').modal('show')
        }
        return
    }
    else {
        enrollInCourse(sectionNumber)
    }
 }

 function enrollInCourse(sectionNumber) {
    // EVENT.TARGET IDENTIFIES THE ENROLL BUTTON THAT WAS PRESSED
    btn = document.getElementById(sectionNumber)
    btnTD = btn.parentElement
    parentTR = btnTD.parentElement
    
    // GET ALL VALUES IN ROW
    tds = parentTR.getElementsByTagName("td");
    sectionNumber = tds[0].innerHTML
    courseNumber = sectionNumber.slice(0,4)
    courseTitle = tds[1].innerHTML
    document.getElementById('modalCoursePrereqTitle').innerHTML = "Prerequistites for " + courseNumber + " (" + courseTitle + ")"


    // HAS MEMBER MORE THAN ONE ENROLLMENT THIS TERM?
    enrollmentsThisTerm = document.getElementById('enrollmentsThisTerm').value
    
    // DATE WHEN MORE THAN 2 ENROLLMENTS ARE ALLOWED
    console.log('get moreThan2... date')
    moreThan2ClassesAllowedDate = new Date(document.getElementById('moreThan2ClassesAllowedDate').value)
    console.log('moreThan2ClassesAllowedDate - '+moreThan2ClassesAllowedDate)

    currentDate = new Date()
    if (enrollmentsThisTerm == 2 & moreThan2ClassesAllowed == 'False') {
        alert("Member may not take more that 2 classes until "+ moreThan2ClassesAllowedDateSTR)
        return
    }

    // ADD TO tblCourse_Enrollees
    memberID = document.getElementById('memberID').value
    $.ajax({
        url: "/addEnrollmentRecord",
        type: "GET",
        data:{term:term,
            sectionNumber:sectionNumber,
            villageID:memberID,
            staffID:staffID
          },
        success: function(data, textStatus, jqXHR)
        {
            if (data.includes('Duplicate')){
                alert(data)
                return
            }
            location.reload()
        },
        error: function (jqXHR, textStatus, errorThrown)
        {
            alert("ERROR - " + textStatus + '\n'+errorThrown)
            
        }
        
    })
    
 }

// HIDE ROWS NOT MATCHING CRITERIA ENTERED
 $("#myInput").on("keyup", function() {
    var value = $(this).val().toLowerCase();
    $("#courseOfferingsTable tr").filter(function() {
      $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
    });
 });
 
function removeEnrollmentRecord(enrollmentID) {
    $.ajax({
        url: "/removeEnrollmentRecord",
        type: "GET",
        data:{recordID:enrollmentID
          },
        success: function(data, textStatus, jqXHR)
        {
            alert('Enrollment record has been removed.')
            location.reload()
        },
        error: function (jqXHR, textStatus, errorThrown)
        {
            alert('ERROR from remove EnrollmentRecord\n'+textStatus+'\n'+errorThrown)
        }
    })
}


function processRegistration(e) {
    console.log('processRegistration rtn')
    // GET SECTION NUMBERS AND MEMBER ID
   
    const enrollmentLines = document.getElementsByClassName('enrollmentLine')
    console.log('# of lines - ',enrollmentLines.length)
    for (let i = 0; i< enrollmentLines.length; i++) {
        const elem = enrollmentLines[i]
        console.log('row - ',enrollmentLines[i])
        console.log('Course # - ',enrollmentLines[i].id)
        // columns = enrollmentLines[i].childNodes
        // for (j=0; j< c.length; j++) {
        //     console.log(columns[j].innerHTML)
        // }
    };
}


function offeringClickRtn(e) {
    if (e.target.className.includes('offeringSectionName')) {
        sectionNumber = e.target.innerHTML
        courseNumber = sectionNumber.slice(0,4)
        courseTitle = e.target.nextElementSibling.innerHTML
        document.getElementById('modalCourseDescriptionTitle').innerHTML = courseNumber + ' - ' + courseTitle
    
        $.ajax({
            url : "/getCourseDescription",
            type: "GET",
            data : {
                courseNumber:courseNumber,
                },
    
            success: function(data, textStatus, jqXHR)
            {
                if (data.courseDescription) {
                    document.getElementById('offeringCourseDescription').innerHTML = data.courseDescription
                }
                else {
                    document.getElementById('offeringCourseDescription').value = 'No description available.'
                }
               
                if (data.msg) {
                    msg = data.msg
                    alert(msg)
                }
            },
            error: function (jqXHR, textStatus, errorThrown) {
                alert("Error getting course description.\n"+errorThrown + '\n'+textStatus)
            }
        }) 
        $('#courseDescriptionModalID').modal('show')   
    }


    if (e.target.className.includes('offeringTitle')) {
        sectionNumber = e.target.previousElementSibling.innerHTML
        courseNumber = sectionNumber.slice(0,4)
        courseTitle = e.target.innerHTML
        document.getElementById('modalCourseNotesTitle').innerHTML = courseNumber + ' - ' + courseTitle
        
        $.ajax({
            url : "/getCourseNotes",
            type: "GET",
            data : {
                courseNumber:courseNumber,
                },
    
            success: function(data, textStatus, jqXHR)
            {
                if (data.courseNote) {
                    document.getElementById('offeringCourseNote').innerHTML = data.courseNote
                }
                else {
                    document.getElementById('offeringCourseNote').value = 'No notes.'
                }
               
                if (data.msg) {
                    msg = data.msg
                    alert(msg)
                }
            },
            error: function (jqXHR, textStatus, errorThrown) {
                alert("Error getting course notes.\n"+errorThrown + '\n'+textStatus)
            }
        }) 
        $('#courseNotesModalID').modal('show')
    }

    
    if (e.target.className.includes('offeringInstructor')) {
        // SHOW LIST OF MEMBERS ENROLLED
        sectionNumber = e.target.previousElementSibling.previousElementSibling.innerHTML
        courseNumber = sectionNumber.slice(0,4)
        sectionID = sectionNumber.slice(5,6)
        courseTitle = e.target.previousElementSibling.innerHTML
        document.getElementById('modalCourseMembersTitle').innerHTML = courseNumber + ' - ' + courseTitle
       
        $.ajax({
            url : "/getCourseMembers",
            type: "GET",
            data : {
                sectionNumber:sectionNumber,
                },
    
            success: function(data, textStatus, jqXHR)
            {
        
                if (data.memberList) {
                    document.getElementById('offeringCourseMembers').innerHTML = data.memberList
                }
                else {
                    document.getElementById('offeringCourseMembers').value = 'No one is enrolled.'
                }
               
                if (data.msg) {
                    msg = data.msg
                    alert(msg)
                }
            },
            error: function (jqXHR, textStatus, errorThrown) {
                alert("Error getting course members.\n"+errorThrown + '\n'+textStatus)
            }
        })     
        $('#courseMembersModalID').modal('show')
    }
}

function updateReceiptNumber(e) {
    memberID = document.getElementById('memberID').value
    receiptNumber = document.getElementById('lightSpeedReceiptNumber').value

    $.ajax({
        url : "/updateReceiptNumber",
        type: "GET",
        data : {
            memberID:memberID,
            receiptNumber:receiptNumber,
            },

        success: function(data, textStatus, jqXHR)
        {
            alert(data.msg)
        },
        error: function (jqXHR, textStatus, errorThrown) {
            alert("Error getting pending records.\n"+errorThrown + '\n'+textStatus)
        }
    })   
}


function notApprovedRtn() {
    alert('Member was not approved to take course')
    $('#coursePrereqModalID').modal('hide')
}

function approvedRtn() {
    sectionNumber = document.getElementById('modalSectionNumber').value
    $('#coursePrereqModalID').modal('hide')
    enrollInCourse(sectionNumber)
}