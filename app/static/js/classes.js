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
    $("#myTable tr").filter(function() {
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
   console.log('openFilterRtn')
    $("#myTable tr").filter(function() {
        $(this).toggle($(this).text().toLowerCase().indexOf('full') <= -1)
        $(this).toggle($(this).text().toLowerCase().indexOf('closed') <= -1)
    })
}
function showAllClasses() {
    console.log('showAllClasses')
     $("#myTable tr").filter(function() {
         // $(this).toggle($(this).text().toLowerCase().indexOf('full') <= -1)
         $(this).toggle()
     })
 }    


// function courseSelectedRtn() {
//     console.log('courseSelectedRtn - '+ this.value)
//     courseData = this.value
//     selectedCourse = courseData.slice(0,4)
//     console.log('Course selected - '+ selectedCourse)
//     termSelected = localStorage.getItem('term',this.value)
//     if (termSelected == None | termSelected == '') {
//         alert('Please select a term.')
//         return
//     }
//     // filter course offerings by course
//     $(this).toggle($(this).text().toLowerCase().indexOf(selectedCourse) <= -1)
//     // apply all or open filter

// }

function termSelectedRtn() {
    localStorage.setItem('term',this.value) 
    termSelected = this.value
    console.log('term selected - ',this.value)
    link = '/classes/ /'+ termSelected
    console.log('link - '+link)
    window.location.href = link
}

$(document).ready(function(){
      $("#myInput").on("keyup", function() {
        console.log('Input - ' + this.value)
        var value = $(this).val().toLowerCase();
        $("#myTable tr").filter(function() {
          $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
        });
      });
    });
    