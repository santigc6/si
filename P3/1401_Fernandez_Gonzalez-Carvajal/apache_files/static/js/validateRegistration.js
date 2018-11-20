function validateRegistration(){
  var user = document.forms["regForm"]["Username"].value;
  var pass = document.forms["regForm"]["Password"].value;
  var rPass = document.forms["regForm"]["RepeatPassword"].value; 
  var email = document.forms["regForm"]["E-mail"].value; 
  var cCard = document.forms["regForm"]["CreditCard"].value;
  
  if (user == "" || user == "Username" || user.includes(" ")) {
    alert("Invalid username");
    return false;
  } else if (pass == "" || pass == "Password" || pass.length < 8){
    alert("Invalid password");
    return false;
  } else if (pass != rPass) {
    alert("Passwords do not match");
    return false;
  } else if (email == "" || email == "E-mail"){
    alert("Invalid email");
    return false
  } 
  if (email.length != 0) {
    var flag=0;
    for(var i = 0; i < email.length; i++){
      if (email[i]=="@"){
        flag++;
      }
    }
    if (flag != 1){
      alert("Invalid email");
      return false;
    }
  } 
  if(cCard == "" || cCard == "Credit card"){
    alert("Invalid visa credit card [it must start with 4 and it must has a length of 13 or 16 digits]");
    return false;
  } else {
    var cardno = /^(?:4[0-9]{12}(?:[0-9]{3})?)$/;
  
    if(cCard.match(cardno)){
      return true;
    }
    alert("Invalid visa credit card [it must start with 4 and it must has a length of 13 or 16 digits]");
    return false;
  }
}
