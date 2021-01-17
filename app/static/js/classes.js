
// SET INTIAL VALUES 

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

// WAS TERM PASSED IN?
term = document.getElementById('termID').innerHTML

// SHOW ENROLL BUTTONS IF MEMBER HAS BEEN SELECTED
memberID = document.getElementById('memberID').value
if (memberID != ''){
    $(".enrollBtn").filter(function() {
        $(this).toggle()
    })
}


// GET LAST USED MEMBER VALUE IF AVAILABLE
// selectedMember = localStorage.getItem('memberSelected')
// if (selectedMember != null & selectedMember != '') {
//     // SET LIST OF MEMBERS TO LAST SELECTED MEMBER
//     document.getElementById('selectMemberID').title = selectedMember
// }
// else{
//     // CLEAR MEMBER VALUE''
//     selectedMember = ''
// }

// SHOW ALL CLASSES

// SET selectedCourse TO BLANK
selectedCourse = ''

// DEFINE EVENT LISTENERS
//document.getElementById("selectTermID").addEventListener("change",termSelectedRtn)
//document.getElementById("selectTermID").addEventListener("click",termSelectedRtn)
document.getElementById("selectMemberID").addEventListener("change",memberSelectedRtn)
document.getElementById("selectMemberID").addEventListener("click",memberSelectedRtn)
//document.getElementsByClassName("dropClassBtn").addEventListener('click',removeCourseRtn)
//document.getElementsByClassName("removeEnrollmentBtn").addEventListener('click',removeEnrollmentRtn)

//document.getElementById('coursesTakenDetail').addEventListener("click",removeCourseRtn)
//document.getElementById('enrollmentDetail').addEventListener('click',removeLineRtn)
//document.getElementById('enrollmentDetail').addEventListener('change',setQtyRtn)
document.getElementById('courseOfferingsTable').addEventListener('click',offeringClickRtn)
document.getElementById('lightspeedBtn').addEventListener('click',updateReceiptNumber)

$("#selectCourseID").on("change", function() {
    courseData = this.value
    selectedCourse = courseData.slice(0,4)
    $("#courseOfferingsTable tr").filter(function() {
        $(this).toggle($(this).text().indexOf(selectedCourse) > -1)
    })
 });
 
$("#approvalOptions").on('click',function(){
    alert('approvalOptions clicked')
    document.getElementById('metPrerequisitesID').removeAttribute('disabled')
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

// function showOpenOnly() {
//     $("#offeringsTable tr").filter(function() {
//         $(this).toggle($(this).text().toLowerCase().indexOf('full') == -1)
//         $(this).toggle($(this).text().toLowerCase().indexOf('closed') == -1)
//     })
// }

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

 function enrollInCourse(event) {

    // EVENT.TARGET IDENTIFIES THE ENROLL BUTTON THAT WAS PRESSED
    btn = event.target
    btnTD = event.target.parentElement
    parentTR = btnTD.parentElement
    
    // GET ALL VALUES IN ROW
    tds = parentTR.getElementsByTagName("td");
    sectionNumber = tds[0].innerHTML
    courseNumber = sectionNumber.slice(0,4)
    document.getElementById('modalCoursePrereqTitle').innerHTML = "Prerequistites for " + courseNumber
    // CHECK FOR PREREQUISITES
    prereqID = 'p' + sectionNumber
    console.log('prereqID - '+prereqID)
    prereq = document.getElementById(prereqID)
    console.log('prereq - '+prereq)
    if (prereq != null) {
        prereqValue = prereq.innerHTML
        console.log('prereqValue - '+prereqValue)
        if (prereqValue != '') {
            document.getElementById('prerequisites').innerHTML = prereqValue
            $('#coursePrereqModalID').modal('show')
        }
        return
    }
    
    // HAS MEMBER MORE THAN ONE ENROLLMENT THIS TERM?
    enrollmentsThisTerm = document.getElementById('enrollmentsThisTerm').value
    console.log('enrollmentsThisTerm - '+enrollmentsThisTerm)

    // DATE WHEN MORE THAN 2 ENROLLMENTS ARE ALLOWED
    console.log('get moreThan2... date')
    moreThan2ClassesAllowedDate = new Date(document.getElementById('moreThan2ClassesAllowedDate').value)
    console.log('moreThan2ClassesAllowedDate - '+moreThan2ClassesAllowedDate)

    currentDate = new Date(today)
    if (enrollmentsThisTerm == 2 & moreThan2ClassesAllowed == 'False') {
        alert("Member may not take more that 2 classes until "+ moreThan2ClassesAllowedDateSTR)
        return
    }

    // ADD TO tblCourse_Enrollees
    console.log('addToEnrollment')
    console.log('staffID - ',staffID)
    memberID = document.getElementById('memberID').value
    console.log('memberID - ',memberID)
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
            // open modal, check prerequisites
           
        },
        error: function (jqXHR, textStatus, errorThrown)
        {
            alert("ERROR - " + textStatus + '\n'+errorThrown)
            
        }
    })
 }


function termSelectedRtn() {
    localStorage.setItem('term',this.value) 
    termSelected = this.value
    console.log('term selected - ',this.value)
    link = '/classes/ /'+ termSelected
    console.log('link - '+link)
    window.location.href = link
}

// HIDE ROWS NOT MATCHING CRITERIA ENTERED
$(document).ready(function(){
      $("#myInput").on("keyup", function() {
        var value = $(this).val().toLowerCase();
        $("#courseOfferingsTable tr").filter(function() {
          $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
        });
      });
    });
 
// REMOVES A LINE FROM REGISTRATION AREA
// function removeLineRtn(e) {
//     if (e.target.type == 'submit'){
//         sectionNumber = e.target.id.slice(3,9)
//         divToDelete = document.getElementById(sectionNumber)
//         divToDelete.remove()
//     }
// }

// REMOVE A COURSE FROM THE COURSES TAKEN AREA
// function removeCourseRtn(e) {
//     console.log('old rtn')
// }

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
    // const enrollmentRows = document.getElementsByClassName('enrollmentDetail')
    // console.log('# of rows - ',enrollmentRows.length)
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
        //parent = document.getElementById('enrollmentDetail')
    
    //var c = parent.childNodes;
    //for (i = 0; i < c.length; i++) {
    //    console.log('... i ... ' + i,c[i].type, c[i].className)
        //console.log(c[i].innerHTML)
   
    //while (parent.firstchild
    // CALL ROUTINE TO ADD RECORDS TO tblCourse_Enrollees

    // PRINT CLASS SCHEDULE

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
    console.log('e - '+ e.target)
    console.log('updateReceiptNumber')
    memberID = document.getElementById('memberID').value
    $.ajax({
        url : "/updateReceiptNumber",
        type: "GET",
        data : {
            memberID:memberID,
            },

        success: function(data, textStatus, jqXHR)
        {
            alert('Transaction number complete.')
        },
        error: function (jqXHR, textStatus, errorThrown) {
            alert("Error getting course notes.\n"+errorThrown + '\n'+textStatus)
        }
    })   
}

$('#coursePrereqModalID').on('show.bs.modal', function () {
    //document.getElementById('prerequisites').innerHTML = 'Prerequisite requirements will go here ...'
    // courseNumber = document()
    // document.getElementById("modalCoursePrereqTitle").value = prereqTitle
})


