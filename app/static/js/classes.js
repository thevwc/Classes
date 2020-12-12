// ON PAGE LOAD ...

// SET INTIAL VALUES 


// DEFINE EVENT LISTENERS
document.getElementById("selectMember").addEventListener("change",memberSelectedRtn)
document.getElementById("selectMember").addEventListener("click",memberSelectedRtn)
document.getElementById("selectCourse").addEventListener("change",courseSelectedRtn)
document.getElementById("selectCourse").addEventListener("click",courseSelectedRtn)

// FUNCTIONS 
function memberSelectedRtn() {
    selectedMember = this.value
    lastEight = selectedMember.slice(-8)
    curMemberID= lastEight.slice(1,7)
    document.getElementById('selectpicker').value=''

    // GET MEMBER NAME AND COURSES TAKEN 
    window.location.href = '/classes?villageID=' + curMemberID 
}

function courseSelectedRtn() {
    selectedMember = this.value
    //lastEight = selectedMember.slice(-8)
    curCourseNumber= selectedMember.slice(0,4)
    

    // Use ajax to get data for course offering table

    //document.getElementById('selectpicker').value=''

    // GET MEMBER NAME AND COURSES TAKEN 
    //window.location.href = '/classes?villageID=' + curMemberID 
}
  