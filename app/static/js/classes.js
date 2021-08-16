// INITIATE TOOLTIPS
$(function () {
    $('[data-toggle="tooltip"]').tooltip()
  })

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
    numberOfClassesEnrolled = document.getElementById('numberOfClassesEnrolled').value 
    document.getElementById('prtScheduleBtn').style.display="block"
    
    // SHOW LIGHTSPEED SECTION
    //document.getElementById('lightSpeedFormID').style.display="block";
}

enrollments = document.getElementById('enrollDetail')
lightSpeedPrtBtn = document.getElementById('lightspeedPrtBtn')
lightSpeedPaidBtn = document.getElementById('lightspeedPaidBtn')

// if (enrollments.childElementCount > 0) {
//     lightSpeedPrtBtn.removeAttribute('disabled')
//     lightSpeedPaidBtn.removeAttribute('disabled')
// }
// else {
//     lightSpeedPrtBtn.setAttribute('disabled','disabled')
//     lightSpeedPaidBtn.setAttribute('disabled','disabled')
// }

// DEFINE EVENT LISTENERS
document.getElementById("selectMemberID").addEventListener("change",memberSelectedRtn)
document.getElementById("selectMemberID").addEventListener("click",memberSelectedRtn)
document.getElementById('courseOfferingsTable').addEventListener('click',offeringClickRtn)
document.getElementById('lightspeedPaidBtn').addEventListener('click',updateReceiptNumber)

$(".enrollBtn").click(function() {
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
    sectionNumber = this.id
    prereqID = 'p'+sectionNumber
    prereq = document.getElementById(prereqID).innerHTML
    if (prereq.includes('Prereq')){
        checkForPrerequisites(this.id)
    }
    else {
        // OK TO ENROLL IN COURSE
        enrollInCourse(sectionNumber,'')
    }
    // document.getElementById('lightspeedPrtBtn').removeAttribute('disabled')
    // document.getElementById('lightspeedPaidBtn').removeAttribute('disabled')
})

// modify this routine to only look at section name in first column
$("#selectCourseID").on("change", function() {
    clearKeywords()
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
    //document.getElementById('lightspeedPrtBtn').removeAttribute('disabled')

    // GET MEMBER NAME AND COURSES TAKEN 
    link = '/classes/?villageID=' + selectedMember
    window.location.href = link

}

function showOpenOnly() {
    $("#courseOfferingsTable tr").show()
    $("#courseOfferingsTable tr[class~='FULL']").hide()    
    $("#courseOfferingsTable tr[class~='CLOSED']").hide()    
    clearKeywords()
    clearSelectCourse()
}

function showAllClasses() {
     $("#courseOfferingsTable tr").filter(function() {
        $(this).show()
        clearKeywords()
        clearSelectCourse()
     })
 }    

function clearKeywords() {
    document.getElementById("keywordID").value = ''
}

function clearSelectCourse() {
    $("#selectCourseID").val('default').selectpicker("refresh");
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
    sectionNumber = tds[0].innerHTML.slice(0,6)
    courseNumber = sectionNumber.slice(0,4)
    shopLocation = tds[1].innerHTML
    courseTitle = tds[2].innerHTML
    courseTitle = courseTitle.trim()
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
    console.log ('ADD TO tblCourse_Enrollees')
    memberID = document.getElementById('memberID').value
    $.ajax({
        url: "/addEnrollmentRecord",
        type: "GET",
        data:{term:term,
            sectionNumber:sectionNumber,
            shopLocation:shopLocation,
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
 $("#keywordID").on("keyup", function() {
    clearSelectCourse()
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
        sectionNumber = e.target.previousElementSibling.previousElementSibling.innerHTML
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
        sectionNumber = e.target.previousElementSibling.previousElementSibling.previousElementSibling.previousElementSibling.innerHTML
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
    //receiptNumber = document.getElementById('lightSpeedReceiptNumber').value
    receiptNumber = 'PAID'
    $.ajax({
        url : "/updateReceiptNumber",
        type: "GET",
        data : {
            memberID:memberID,
            receiptNumber:receiptNumber,
            },

        success: function(data, textStatus, jqXHR)
        {
            msg = data.msg
            
            if (msg.slice(0,5) == 'ERROR'){
                modalAlert('ERROR UPDATING RECEIPT STATUS',msg)
            }
            else {
                modalAlert('RECEIPT STATUS',msg)
                location.reload()
            }
            

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


function prtMemberSchedule(){
    link = "/prtMemberSchedule/" + memberID 
    window.location.href = link
}

function prtEnrollmentReceipt(){
    //document.getElementById('lightspeedPaidBtn').setAttribute('disabled','disabled')
    link = "/prtEnrollmentReceipt/" + memberID 
    window.location.href = link
}