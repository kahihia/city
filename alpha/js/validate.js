// JavaScript Document
browser_version= parseInt(navigator.appVersion);
browser_type = navigator.appName;
if (browser_type == "Microsoft Internet Explorer" && (browser_version >= 4)) {
document.write("<link REL='stylesheet' HREF='/static/styles/styles_ie.css' TYPE='text/css'>");
}
else {
document.write("<link REL='stylesheet' HREF='/static/styles/styles.css' TYPE='text/css'>");
}

function validate(form_id,email) {
   var reg = /^([A-Za-z0-9_\-\.])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,4})$/;
   var address = document.forms[form_id].elements[email].value;
   var lowercaseAddress = address.toLowerCase();
   var email = document.getElementById("email");
   if(reg.test(address) == false) {
      alert('Please enter a valid email address!');
      return false;
   }
}

function validate_tracking_no(field,alerttxt)
{
with (field)
  {
  tracking_no=value.toString();
    if (value==null||isNaN(value)==true||tracking_no[(tracking_no.length)-1]==" "||tracking_no[0]==" "||tracking_no[1]=="x"||tracking_no[1]=="X")
    {
    alert(alerttxt);return false;
    }
	else if(value.indexOf(".")>-1){
		alert(alerttxt);return false;
	}
  else
    {
    return true;
    }
  }
}

function limitText(limitField, limitCount, limitNum) {
	if (limitField.value.length > limitNum) {
		limitField.value = limitField.value.substring(0, limitNum);
	} else {
		limitCount.value = limitNum - limitField.value.length;
	}
}

function validate_email(field,alerttxt)
{
with (field)
  {
apos=value.indexOf("@");
dotpos=value.lastIndexOf(".");
if (apos<1||dotpos-apos<2)
    {
	alert(alerttxt);return false;
	}
  else {return true;}
  }
}

function trim(str)
   {
    s = str.replace(/^(\s)*/, '');
     s = s.replace(/(\s)*$/, '');
    return s;
   }


function validate_required(field,alerttxt)
{
with (field)
  {
  if (value==null||value=="")
    {
    alert(alerttxt);return false;
    }	
  else
    {
    return true;
    }
  }
}

//Events Form validation form
function validate_form_events(thisform)
  {
with (thisform)
  {
  if (validate_required(events_name,"Please fill in the box ``Events Name``")==false)
  {events_name.focus();return false;}
  }
with (thisform)
  {
  if (validate_required(events_loc,"Please fill in the box ``Events Location``")==false)
  {events_loc.focus();return false;}
  }
}


//Feedback validation form
function validate_form_feedback(thisform)
  {
with (thisform)
  {
  if (validate_required(feedback_name,"Please fill in the box ``Feedback Name``")==false)
  {feedback_name.focus();return false;}
  }  
with (thisform)
  {
  if (validate_required(email,"Please fill in the box ``Email``")==false)
  {email.focus();return false;}
  }
with (thisform)
  {
  if (validate_email(email,"Please enter a valid email address!")==false)
    {email.focus();return false;}
  }
}

//Taggle
function toggle_visibility(id) {
   var e = document.getElementById(id);
   if(e.style.display == 'block')
	  e.style.display = 'none';
   else
	  e.style.display = 'block';
}
//Field Validation
