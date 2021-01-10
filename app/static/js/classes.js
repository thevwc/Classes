// SET INTIAL VALUES 

// was term passed in?
term = document.getElementById('termID').innerHTML
console.log('term from page - ' + term)

if (term == ''){
    // GET LAST USED TERM VALUE IF AVAILABLE
    storedTerm = localStorage.getItem('term')
    if (storedTerm != null & storedTerm != '') {
        // SET LIST OF TERMS TO LAST USED TERM
        document.getElementById('selectTermID').title = storedTerm
        term = storedTerm
    }
    else{
        // CLEAR TERM VALUE''
        term = ''
        document.getElementById('selectTermID').title = ''
    }
}
else {
    console.log('set title ...')
    document.getElementById('selectTermID').title = term
}

// GET LAST USED MEMBER VALUE IF AVAILABLE
selectedMember = localStorage.getItem('memberSelected')
if (selectedMember != null & selectedMember != '') {
    // SET LIST OF MEMBERS TO LAST SELECTED MEMBER
    document.getElementById('selectMemberID').title = selectedMember
}
else{
    // CLEAR MEMBER VALUE''
    selectedMember = ''
}

// SHOW ALL CLASSES

// SET selectedCourse TO BLANK
selectedCourse = ''

// DEFINE EVENT LISTENERS
document.getElementById("selectTermID").addEventListener("change",termSelectedRtn)
document.getElementById("selectTermID").addEventListener("click",termSelectedRtn)
document.getElementById("selectMemberID").addEventListener("change",memberSelectedRtn)
document.getElementById("selectMemberID").addEventListener("click",memberSelectedRtn)

$("#selectCourseID").on("change", function() {
    courseData = this.value
    selectedCourse = courseData.slice(0,4)
    $("#offeringsTable tr").filter(function() {
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
    //console.log('link - '+link)
    window.location.href = link

}

function showOpenOnly() {
    $("#offeringsTable tr").filter(function() {
        $(this).toggle($(this).text().toLowerCase().indexOf('full') == -1)
        $(this).toggle($(this).text().toLowerCase().indexOf('closed') == -1)
    })
}
function showAllClasses() {
     $("#offeringsTable tr").filter(function() {
         // $(this).toggle($(this).text().toLowerCase().indexOf('full') <= -1)
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
    title = tds[1].innerHTML
    instructor = tds[2].innerHTML
    fee = tds[7].innerHTML
    suppliesFee = tds[9].innerHTML

    // BUILD ROW IN ENROLL TABLE
    enrollTable = document.getElementById('myEnrollmentTable')
    enrollRow = document.createElement('tr')
    enrollRow.setAttribute('id',sectionNumber)
    // APPEND ROW TO END OF ENROLL TABLE
    enrollTable.appendChild(enrollRow)
    
    // CREATE TD FOR SECTION NUMBER
    sectionTD = document.createElement('td')
    sectionTD.appendChild(document.createTextNode(sectionNumber))
    enrollTable.appendChild(sectionTD)

    titleTD = document.createElement('td')
    titleTD.appendChild(document.createTextNode(title))
    enrollTable.appendChild(titleTD)

    instructorTD = document.createElement('td')
    instructorTD.appendChild(document.createTextNode(instructor))
    enrollTable.appendChild(instructorTD)

    feeTD = document.createElement('td')
    feeTD.appendChild(document.createTextNode(fee))
    enrollTable.appendChild(feeTD)

    suppliesfeeTD = document.createElement('td')
    suppliesfeeTD.appendChild(document.createTextNode(suppliesFee))
    enrollTable.appendChild(suppliesfeeTD)
  
    setsTD = document.createElement('td')
    enrollTable.appendChild(setsTD)
    qtyInput = document.createElement('input')
    qtyInput.className = 'setsQty'
    qtyInput.setAttribute("type","number")
    qtyInput.setAttribute("width",'20px')
    qtyInput.setAttribute("value",1)
    setsTD.appendChild(qtyInput)
 
    extPriceTD = document.createElement('td')
    extPriceTD.appendChild(document.createTextNode(' '))
    enrollTable.appendChild(extPriceTD)

    removeTD = document.createElement('td')
    enrollTable.appendChild(removeTD)
    removeBtn = document.createElement('button')
    removeBtn.setAttribute('id','btn'+sectionNumber)
    removeBtn.className = 'btn btn-primary btn-sm btnRemove'
    removeBtn.onclick=removeEnrollmentRow
    removeBtn.appendChild(document.createTextNode('REMOVE'))
    removeTD.appendChild(removeBtn)

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
        console.log('Input - ' + this.value)
        var value = $(this).val().toLowerCase();
        $("#offeringsTable tr").filter(function() {
          $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
        });
      });
    });
 
    
// $("#enrollment").on('click','.btnRemove', function(r) {
//     console.log('btnRemove rtn')
//     console.log('this - '+this)
//     var i = r.parentNode.parentNode.rowIndex;
//     console.log('i - '+i)
//     document.getElementById("enrollment").deleteRow(i)

//     element = $(this).closest
//     console.log('closest - '+element)
//     $(this).closest('tr').remove();
// })

// function removeTest(e){
//     btnID = e.target.id 
//     rowID = btnID.slice(3,9)
//     var row = document.getElementById(rowID)
//     row.parentNode.removeChild(row)
// }

    
    
function removeEnrollmentRow(e) {
    enrollTable = document.getElementById('enrollment')
    console.log('table - ',enrollTable)
    // EVENT.TARGET IDENTIFIES THE REMOVE BUTTON THAT WAS PRESSED
    btnID = e.target.id 
    // GET SECTION NUMBER FROM BUTTON ID
    console.log('btnID - ',btnID)
    rowID = btnID.slice(3,9)
    console.log('rowID - ',rowID)

    // GET TR ELEMENT
    rowToDelete = document.getElementById(rowID)
    console.log('row to delete - ',rowToDelete)
    // GET TR ELEMENT BY ID OF TR; RETRIEVE ROWINDEX FROM TR ELEMENT
    rowNumber = document.getElementById(rowID).rowIndex
    console.log('row index - ',rowNumber )

    // DELETE ROW FROM TABLE USING ROWINDEX

    enrollTable.deleteRow(rowToDelete)
    //rowToDelete.parentNode.removeChild(rowToDelete)
}