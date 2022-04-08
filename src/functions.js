//Registration functions
function confirm_registration(){
    let email = document.getElementById("email_input");
    if(email.value === ""){
        window.alert("Please enter your email.");
    }
    let username = document.getElementById("username_input");
    let password = document.getElementById("password_input");
    let password_confirmation = document.getElementById("password_confirmation");
    if(password.value === password_confirmation.value){
        window.location.href = "/login";
    } else {
        document.getElementById("registration-form").event.preventDefault();
        window.alert("The passwords do not match. Please re-enter your password.");
    }
}