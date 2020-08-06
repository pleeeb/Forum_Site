"use strict"
window.onload = function(){
	var claimModal = document.getElementById("claimModal");
	var loginModal = document.getElementById("loginModal");
	var signModal = document.getElementById("signModal");
	var btn = document.getElementById("myBtn");
	var claimclose = document.getElementById("claimspan");
	var loginclose = document.getElementById("loginspan");
	var loginname = document.getElementById("loginu");
	var loginpass = document.getElementById("loginp");
	var signclose = document.getElementById("signspan");
	var signSel = document.getElementById("signupSelect");
	var signname = document.getElementById("signupu");
	var signemail = document.getElementById("signupe");
	var signpass = document.getElementById("signupp");
	var signmsg = document.getElementById("msg");
	var usercheck= document.getElementById("statusmsg");
	var emailcheck= document.getElementById("statusEmsg");
	var signform = document.getElementById("signform");
	var topicList = document.getElementById("topicList");
	var delUser = document.getElementById("delUser");
	
	claimclose.onclick = function(){
		claimModal.style.display = "none";
	}
	
	loginclose.onclick = function(){
		loginModal.style.display = "none";
	}
	
	signclose.onclick = function(){
		signModal.style.display = "none";
	}
	
	window.onclick = function(event){
		if(event.target == claimModal){
			claimModal.style.display = "none";
		}
		else if(event.target == loginModal){
			loginModal.style.display = "none";
		}
		else if(event.target == signModal){
			signModal.style.display = "none";
		}
		else if(event.target == topicList){
			topicList.style.display = "none";
		}
		else if(event.target == delUser){
			delUser.style.display = "none";
		}
	}
	
	signname.addEventListener('input', () =>{
		if (signname.validity.patternMismatch){
			signname.setCustomValidity("Username must be between 3 and 20 characters");
		}
		else{
			signname.setCustomValidity("");
		}
	});

	signemail.addEventListener('input', () =>{
		if (signemail.validity.patternMismatch){
			signemail.setCustomValidity("Please enter a valid email address");
		}
		else{
			signemail.setCustomValidity("");
		}
	});
	
	signpass.addEventListener('input', () =>{
		if (signpass.validity.patternMismatch){
			signpass.setCustomValidity("Password must be between 5 and 20 characters long and contain a lowercase letter, uppercase letter and digit");
		}
		else{
			signpass.setCustomValidity("");
		}
	});
}

function LoginSelect(){
		loginModal.style.display = "block";
		var loginname = document.getElementById("loginu");
		var loginpass = document.getElementById("loginp");
		loginname.value = "";
		loginpass.value = "";
	}
	
function SignSelect(){
		var usercheck= document.getElementById("statusmsg");
		var emailcheck= document.getElementById("statusEmsg");
		var signname = document.getElementById("signupu");
		var signemail = document.getElementById("signupe");
		var signpass = document.getElementById("signupp");
		signModal.style.display = "block";
		usercheck.style.visibility = "hidden";
		emailcheck.style.visibility = "hidden";
		signname.value = "";
		signemail.value = "";
		signpass.value = "";
	}
	
function CreateClaim(){
		claimModal.style.display = "block";
		var claimType = document.getElementById("claimType");
		claimType.value = "norelate"
}


	







