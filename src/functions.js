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

function load() {
    var page_cookie = document.cookie.split('; ');
    var cookie_dict = {};
    for(i = 0; i < page_cookie.length; i++){
        var cookie = page_cookie[i].split("=");
        cookie_dict[cookie[0]] = cookie[1];
    }
    console.log(cookie_dict);
    if("xsrf_token" in cookie_dict){
        document.getElementById("token").innerHTML += '<input value="' + cookie_dict["xsrf_token"] + '" name="xsrf_token" hidden>';
    }
}

function welcome() {
    var page_cookie = document.cookie.split('; ');
    var cookie_dict = {};
    for(i = 0; i < page_cookie.length; i++){
        var cookie = page_cookie[i].split("=");
        cookie_dict[cookie[0]] = cookie[1];
    }
    console.log(cookie_dict);
    if("username" in cookie_dict){
        document.getElementById("welcome-text").innerHTML += '<h1 class="welcome-message">Welcome, ' + cookie_dict["username"] + '!</h1>';
    }
}