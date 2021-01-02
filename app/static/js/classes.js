// ON PAGE LOAD ...
//console.log('page load')
// SET INTIAL VALUES 

// GET LAST USED TERM VALUE IF AVAILABLE
selectedTerm = localStorage.getItem('term')
if (selectedTerm != null & selectedTerm != '') {
    // SET LIST OF TERMS TO LAST USED TERM
    document.getElementById('selectTermID').title = selectedTerm
}
else{
    // CLEAR TERM VALUE''
    selectedTerm = ''
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

// SET selectedCourse TO BLANK
selectedCourse = ''

// DEFINE EVENT LISTENERS
document.getElementById("selectTermID").addEventListener("change",termSelectedRtn)
document.getElementById("selectTermID").addEventListener("click",termSelectedRtn)
document.getElementById("selectMemberID").addEventListener("change",memberSelectedRtn)
document.getElementById("selectMemberID").addEventListener("click",memberSelectedRtn)
document.getElementById("selectCourseID").addEventListener("change",courseSelectedRtn)
document.getElementById("selectCourseID").addEventListener("click",courseSelectedRtn)

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

function courseSelectedRtn() {
    console.log('courseSelectedRtn - '+ this.value)
    courseData = this.value
    selectedCourse = courseData.slice(0,4)
    console.log('Course selected - '+ selectedCourse)
    

    // Use ajax to get data for course offering table

    //document.getElementById('selectpicker').value=''

    // GET MEMBER NAME AND COURSES TAKEN 
    //window.location.href = '/classes?villageID=' + selectedMember 
}

function termSelectedRtn() {
    localStorage.setItem('term',this.value) 
    //document.getElementById('termSelected').value = this.value
}
  