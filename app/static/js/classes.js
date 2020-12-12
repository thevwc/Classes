// ON PAGE LOAD ...
cancelBtn = document.getElementById('cancelBtn')
saveBtn = document.getElementById('saveBtn')
applicant = document.getElementById('applicantID')
applicationStatus = document.getElementById('applicationStatusID')
memberIDelement = document.getElementById('memberID')
waitListForm = document.getElementById('waitListFormID')
memberIDbtn = document.getElementById('memberID')


// SET INTIAL VALUES 
if (memberIDelement.value.length > 0) {
  memberIDelement.readonly = true
  document.getElementById('printConfirmBtnID').removeAttribute('disabled')
}
else {
  memberIDelement.readonly = false
  selectAllMonths()
  document.getElementById('state').value = 'FL'
  document.getElementById('dtEntered').style.display='none'
}

// HIDE CANCEL AND SAVE BUTTONS
cancelBtn.style.display='none'
saveBtn.style.display='none'

// DEFINE EVENT LISTENERS
document.getElementById("selectMember").addEventListener("change",memberSelectedRtn)
document.getElementById("selectMember").addEventListener("click",memberSelectedRtn)
document.getElementById("selectCourse").addEventListener("change",courseSelectedRtn)
document.getElementById("selectCourse").addEventListener("click",courseSelectedRtn)


applicant.addEventListener("change",applicantDataChanged)
applicationStatus.addEventListener("change",applicantStatusDataChanged)


// FUNCTIONS 
function memberSelectedRtn() {
    selectedMember = this.value
    lastEight = selectedMember.slice(-8)
    currentMemberID= lastEight.slice(1,7)
    document.getElementById('selectpicker').value=''

    // SET UP LINK TO waitList FORM 
    var linkToWaitListBtn = document.getElementById('linkToWaitList');
    link='/waitlist/' + currentMemberID 
    linkToWaitListBtn.setAttribute('href', link)
    linkToWaitListBtn.click()
}


// function showMenu() {
//     document.getElementById("myDropdown").classList.toggle("show");
//   }

function applicantDataChanged() {
    if (memberIDelement.value != "") {
      document.getElementById('cancelBtn').style.display='inline'
      document.getElementById('saveBtn').style.display='inline'
      
    }
    else {
      alert("Please enter a member ID.")
    }   
}

function applicantStatusDataChanged() {
  if (memberIDelement.value != '' ) {
    document.getElementById('cancelBtn').style.display='inline'
    document.getElementById('saveBtn').style.display='inline'
  }
  else {
    alert("Please enter a member ID.")
  }
}

document.querySelector('#monthCheckboxesID').onclick = function(ev) {
  inputID = ev.target.id
  console.log('inputID - '+ inputID)
  if (ev.target.checked) {
      document.getElementById(inputID).value='True'
  }
  else {
      document.getElementById(inputID).value='False' 
  }
}

function newApplicant() {
  // SET UP LINK TO waitList FORM 
  var linkToWaitListBtn = document.getElementById('linkToWaitList');
  link='/waitlist'  
  linkToWaitListBtn.setAttribute('href', link)
  linkToWaitListBtn.click()
}

function printConfirmation() {
  // SET UP LINK TO waitList FORM 
  var linkToPrintConfirmationBtn = document.getElementById('linkToPrintConfirmation');
  memberID=document.getElementById('memberID').value 
  link='/printConfirmation/'  + memberID
  linkToPrintConfirmationBtn.setAttribute('href', link)
  linkToPrintConfirmationBtn.click()
}

$('input[type="tel"]')
	.keydown(function (e) {
		var key = e.which || e.charCode || e.keyCode || 0;
		$phone = $(this);

    // Don't let them remove the starting '('
    if ($phone.val().length === 1 && (key === 8 || key === 46)) {
			$phone.val('('); 
      return false;
		} 
    // Reset if they highlight and type over first char.
    else if ($phone.val().charAt(0) !== '(') {
			$phone.val('('+String.fromCharCode(e.keyCode)+''); 
		}

		// Auto-format- do not expose the mask as the user begins to type
		if (key !== 8 && key !== 9) {
			if ($phone.val().length === 4) {
				$phone.val($phone.val() + ')');
			}
			if ($phone.val().length === 5) {
				$phone.val($phone.val() + ' ');
			}			
			if ($phone.val().length === 9) {
				$phone.val($phone.val() + '-');
			}
		}

		// Allow numeric (and tab, backspace, delete) keys only
		return (key == 8 || 
				key == 9 ||
				key == 46 ||
				(key >= 48 && key <= 57) ||
				(key >= 96 && key <= 105));	
	})
	
	.bind('focus click', function () {
		$phone = $(this);
		
		if ($phone.val().length === 0) {
			$phone.val('(');
		}
		else {
			var val = $phone.val();
			$phone.val('').val(val); // Ensure cursor remains at the end
		}
	})
	
	.blur(function () {
		$phone = $(this);
		
		if ($phone.val() === '(') {
			$phone.val('');
		}
  });
  
  function selectAllMonths() {
    jan=document.getElementById('jan')
    feb=document.getElementById('feb')
    mar=document.getElementById('mar')
    apr=document.getElementById('apr')
    may=document.getElementById('may')
    jun=document.getElementById('jun')
    jul=document.getElementById('jul')
    aug=document.getElementById('aug')
    sep=document.getElementById('sep')
    oct=document.getElementById('oct')
    nov=document.getElementById('nov')
    dec=document.getElementById('dec')
    jan.setAttribute('checked','checked')
    jan.value = 'True'
    feb.setAttribute('checked','checked')
    feb.value = 'True'
    mar.setAttribute('checked','checked')
    mar.value = 'True'
    apr.setAttribute('checked','checked')
    apr.value = 'True'
    may.setAttribute('checked','checked')
    may.value = 'True'
    jun.setAttribute('checked','checked')
    jun.value = 'True'
    jul.setAttribute('checked','checked')
    jul.value = 'True'
    aug.setAttribute('checked','checked')
    aug.value = 'True'
    sep.setAttribute('checked','checked')
    sep.value = 'True'
    oct.setAttribute('checked','checked')
    oct.value = 'True'
    nov.setAttribute('checked','checked')
    nov.value = 'True'
    dec.setAttribute('checked','checked')
    dec.value = 'True'
    
    // THE FOLLOWING CODE SHOULD WORK!
    // var monthBoxes = document.querySelectorAll('.monthCheckboxes input')
    // for (var i = 0; i > monthBoxes.length; i++) {
    //   monthBoxes[i].setAttribute('checked','checked')
    //   monthBoxes[i].value = 'True'
    // }   
  }