// INITIATE TOOLTIPS
$(function () {
    $('[data-toggle="tooltip"]').tooltip()
  })


//GET STAFF ID
//staffID = document.getElementById('staffID').value


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
term = document.getElementById('termID').value

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

$(".enrollBtn").click(function() {
    console.log('enrollBtn clicked ...')
    moreThan2ClassesAllowed = document.getElementById('moreThan2ClassesAllowed').value
    if (moreThan2ClassesAllowed != 'True'){
        numberEnrolled = document.getElementById('enrollDetail').childElementCount
        dateAllowed = document.getElementById('moreThan2ClassesAllowedDate').value
        if (numberEnrolled > 1) {
            modalAlert("ENROLLMENT","More than two classes are not allowed until "+dateAllowed + '.')
            return
        }
    }
    // ARE THERE PREREQUISITES? 
    alert('this.id - ' + this.id)
     
    sectionNumber = this.id
    alert('sectionNumber - '+ sectionNumber)  

    prereqID = 'p'+sectionNumber
    console.log('prereqID - '+ prereqID)
    prereq = document.getElementById(prereqID).innerHTML
    console.log('prereq - |'+ prereq + '|')
    if (prereq != null && prereq != '') {
        console.log('call checkForPrerequisites')
        checkForPrerequisites(this.id)
    }
    else {
        // OK TO ENROLL IN COURSE
        console.log('skip check for prerequisites')
        enrollInCourse(sectionNumber,'')
    }
})

// modify this routine to only look at section name in first column
$("#selectCourseID").on("change", function() {
    courseData = this.value
    selectedCourse = courseData.slice(0,4)

    $("#courseOfferingsTable tr").filter(function() {
        //$(this).toggle($(this).text().indexOf(selectedCourse) > -1)
        $(this).toggle($(this).find("td:eq(0)").text().indexOf(selectedCourse) > -1)
    })
});

function hideRows(input) {
    var input, filter, table, tr, td, i, txtValue;
    filter = input.toUpperCase
    
    table = document.getElementById("courseOfferingsDetail");
    tr = table.getElementsByTagName("tr");
    for (i = 0; i < tr.length; i++) {
        sectionName = tr[i].firstElementChild
        filter = sectionName.innerHTML.slice(0,4)
        td = tr[i].getElementsByTagName("td")[0];

        if (td.innerHTML.slice(0,4) == filter ){
            tr[i].style.display = "";
            } 
        else {
                tr[i].style.display = "none";
            }
    }       
    
}

// FUNCTIONS 
function memberSelectedRtn() {
    memberData = this.value
    localStorage.setItem('memberSelected',this.value) 
    lastEight = memberData.slice(-8)
    selectedMember= lastEight.slice(1,7)

    // GET MEMBER NAME AND COURSES TAKEN 
    link = '/classes/?villageID=' + selectedMember
    window.location.href = link

}

function showOpenOnly() {
    $(".FULL, .CLOSED").filter(function() {
        $(this).toggle()
    })
}

function showAllClasses() {
     $("#courseOfferingsTable tr").filter(function() {
        $(this).show()
        document.getElementById("myInput").value = ''
     })
 }    

 function checkForPrerequisites(sectionNumber) {
    btn = document.getElementById(sectionNumber)
    btnTD = btn.parentElement
    parentTR = btnTD.parentElement
    
    // GET ALL VALUES IN ROW
    tds = parentTR.getElementsByTagName("td");
    courseNumber = sectionNumber.slice(0,4)
    courseTitle = tds[1].innerHTML
    document.getElementById('modalCoursePrereqTitle').innerHTML = "Prerequistites for " + courseNumber + " (" + courseTitle + ")"
    document.getElementById('modalSectionNumber').value = sectionNumber 
    
    // SHOW PREREQUISITES
    // HAS MEMBER MET PREREQUISITE REQUIREMENTS?
    $('#coursePrereqModalID').modal('show')
    return

 }

 function enrollInCourse(sectionNumber,approval) {
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
    moreThan2ClassesAllowedDate = new Date(document.getElementById('moreThan2ClassesAllowedDate').value)
    currentDate = new Date()
    if (enrollmentsThisTerm == 2 & moreThan2ClassesAllowed == 'False') {
        modalAlert("ENROLLMENT","Member may not take more that 2 classes until "+ moreThan2ClassesAllowedDateSTR)
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
            approval:approval
          },
        success: function(data, textStatus, jqXHR)
        {
            if (data.includes('Duplicate')){
                modalAlert("ENROLLMENT",data)
                return
            }
            location.reload()
        },
        error: function (jqXHR, textStatus, errorThrown)
        {
            modalAlert("ENROLLMENT","ERROR - " + textStatus + '\n'+errorThrown)
            
        }
        
    })
    
 }

// HIDE ROWS NOT MATCHING CRITERIA ENTERED
 $("#myInput").on("keyup", function() {
    var value = $(this).val().toLowerCase();
    $("#courseOfferingsDetail tr").filter(function() {
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
            modalAlert('ENROLLMENT','Enrollment record has been removed.')
            // add wait ??
            location.reload()
        },
        error: function (jqXHR, textStatus, errorThrown)
        {
            modalAlert('ENROLLMENT','ERROR from remove EnrollmentRecord\n'+textStatus+'\n'+errorThrown)
        }
    })
}


function processRegistration(e) {
    // GET SECTION NUMBERS AND MEMBER ID
    const enrollmentLines = document.getElementsByClassName('enrollmentLine')
    for (let i = 0; i< enrollmentLines.length; i++) {
        const elem = enrollmentLines[i]
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
                    modalAlert('COURSE DESCRIPTION',msg)
                }
            },
            error: function (jqXHR, textStatus, errorThrown) {
                modalAlert("COURSE DESCRIPTION","Error getting course description.\n"+errorThrown + '\n'+textStatus)
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
                    modalAlert('COURSE NOTES',msg)
                }
            },
            error: function (jqXHR, textStatus, errorThrown) {
                modalAlert('COURSE NOTES',"Error getting course notes.\n"+errorThrown + '\n'+textStatus)
            }
        }) 
        $('#courseNotesModalID').modal('show')
    }

    
    if (e.target.className.includes('offeringInstructor')) {
        // SHOW LIST OF MEMBERS ENROLLED
        sectionNumber = e.target.previousElementSibling.previousElementSibling.previousElementSibling.innerHTML
        courseNumber = sectionNumber.slice(0,4)
        sectionID = sectionNumber.slice(5,6)
        courseTitle = e.target.previousElementSibling.previousElementSibling.innerHTML
        document.getElementById('modalCourseMembersTitle').innerHTML = 
            sectionNumber.slice(0,6) + "<span style='white-space: pre-line'>" + courseTitle + "</span>"
       
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
                    modalAlert('COURSE MEMBERS',msg)
                }
            },
            error: function (jqXHR, textStatus, errorThrown) {
                modalAlert('COURSE MEMBERS',"Error getting course members.\n"+errorThrown + '\n'+textStatus)
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
            modalAlert('UPDATE RECEIPT',data.msg)
        },
        error: function (jqXHR, textStatus, errorThrown) {
            modalAlert('UPDATE RECEIPT',"Error getting pending records.\n"+errorThrown + '\n'+textStatus)
        }
    })   
}


$('#coursePrereqModalID').on('hide.bs.modal', function() {
    itemSelected = document.getElementById('approvalSelected')
    if (itemSelected.value == 'NOT APPROVED') {
        return
    }
    if (itemSelected.value == 'Other'){
        approvalText = document.getElementById('approvalText').value
        if (approvalText == null | approvalText == ''){
            modalAlert('PREREQUISITE APPROVAL','You must enter the reason for approval.')
            return
        }
    }
    else {
        approvalText = itemSelected.value
    }
    // RESET DEFAULT OPTION
    itemSelected.value = 'NOT APPROVED'
    // OK TO ENROLL IN COURSE
    enrollInCourse(sectionNumber,approvalText)
})    
 
function modalAlert(title,msg) {
	document.getElementById("modalTitle").innerHTML = title
	document.getElementById("modalBody").innerHTML= msg
	$('#myModalMsg').modal('show')
}
	
function closeModal() {
	$('#myModalMsg').modal('hide')
}
