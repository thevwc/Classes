
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

// if (term == ''){
//     // GET LAST USED TERM VALUE IF AVAILABLE
//     storedTerm = localStorage.getItem('term')
//     if (storedTerm != null & storedTerm != '') {
//         // SET LIST OF TERMS TO LAST USED TERM
//         document.getElementById('selectTermID').title = storedTerm
//         term = storedTerm
//     }
//     else{
//         // CLEAR TERM VALUE''
//         term = ''
//         document.getElementById('selectTermID').title = ''
//     }
// }
// else {
//     document.getElementById('selectTermID').title = term
// }

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
    // title = tds[1].innerHTML
    // instructor = tds[2].innerHTML
    // fee = tds[7].innerHTML
    // suppliesFee = tds[9].innerHTML

    // feeAmt = parseFloat(fee.substring(fee.indexOf('$') + 1))
    // suppliesFeeAmt = parseFloat(suppliesFee.substring(suppliesFee.indexOf('$') + 1))
    // totalFee = feeAmt + suppliesFeeAmt
    
    // BUILD ROW IN ENROLL TABLE
    // enrollDetail = document.getElementById('enrollmentDetail')
    // enrollRow = document.createElement('div')
    // enrollRow.id = sectionNumber
    // enrollRow.className = 'row enrollmentLine'
    // enrollDetail.appendChild(enrollRow)

    // sectionCol = document.createElement('div')
    // sectionCol.className = 'col-1'
    // sectionCol.innerHTML = sectionNumber
    // enrollRow.appendChild(sectionCol)

    // titleCol = document.createElement('div')
    // titleCol.className = 'col-2'
    // titleCol.innerHTML = title
    // enrollRow.appendChild(titleCol)

    // instructorCol = document.createElement('div')
    // instructorCol.className = 'col-2'
    // instructorCol.innerHTML = instructor
    // enrollRow.appendChild(instructorCol)

    // feeCol = document.createElement('div')
    // feeCol.className = 'col-1'
    // feeCol.innerHTML = fee
    // enrollRow.appendChild(feeCol)

    // suppliesFeeCol = document.createElement('div')
    // suppliesFeeCol.className = 'col-1'
    // suppliesFeeCol.innerHTML = suppliesFee
    // enrollRow.appendChild(suppliesFeeCol)

    // extPriceCol = document.createElement('div')
    // extPriceCol.setAttribute('id','extPrice'+sectionNumber)
    // extPriceCol.className = 'col-1 extPrice'
    // extPriceCol.innerHTML = "$ " + totalFee.toFixed(2)
    // enrollRow.appendChild(extPriceCol)

    // deleteCol = document.createElement('div')
    // deleteCol.className = 'col-1'
    // enrollRow.appendChild(deleteCol)

    // deleteBtn = document.createElement('button')
    // deleteBtn.setAttribute('id','btn'+sectionNumber)
    // deleteBtn.className = 'btn btn-secondary btn-sm removeBtn'
    // deleteBtn.innerHTML = "REMOVE"
    // deleteCol.appendChild(deleteBtn)   
    
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
            $('#courseNotesModalID').modal('show')
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
        console.log ('sectionName clicked')
        
    }
    if (e.target.className.includes('offeringTitle')) {
        console.log('prev sib - ',e.target.previousElementSibling.innerHTML)
        console.log ('title clicked')
        sectionNumber = e.target.previousElementSibling.innerHTML
        courseNumber = sectionNumber.slice(0,4)
        console.log('courseNumber - ',courseNumber)
        courseTitle = e.target.innerHTML
        document.getElementById('modalCourseTitle').innerHTML = courseNumber + ' - ' + courseTitle
        note = '<h1>HEADING</h1>'
        $.ajax({
            url : "/getCourseNotes",
            type: "GET",
            data : {
                courseNumber:courseNumber,
                },
    
            success: function(data, textStatus, jqXHR)
            {
                alert('data.courseNote - '+data.courseNote)
                if (data.courseNote) {
                    note = data.courseNote
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
        n = document.getElementById('offeringCourseNote')
        n.innerHTML = note
        document.getElementById('noteID').value = note
        alert(note)
        document.getElementById('modalCourseTitle').innerHTML = 'TEST TITLE'
        $('#courseNotesModalID').modal('show')

    }
    if (e.target.className.includes('offeringInstructor')) {
        console.log ('instructor clicked')
        // show list of students enrolled
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