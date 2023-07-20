/**
 * Created by Ashar on 7/1/2020.
 */

SignUp = function (data) {
    this.sign_up_url = data.sign_up_url;
    this.login_url = data.login_url;
    this.home_url = data.home_url;
    this.next = null;
    const self = this;

    $("#signupForm").on('submit', function (e) {
        e.preventDefault();
        self.SignUpFormSubmit();
    })

    $("#loginForm").on('submit', function (e) {
        e.preventDefault();
        console.log("Submit");
        self.LoginUpFormSubmit();
    })
};


SignUp.prototype.SignUpFormSubmit = function () {
    var self = this;
    let email = $("#email").val();
    let password = $("#password").val();
    let first_name = $("#first_name").val();
    let last_name = $("#last_name").val();
        if (!first_name){
        genericSweetAlert("Error", 'primeiro nome é necessário', 'error')
        return
    }
    if (!last_name){
        genericSweetAlert("Error", 'Sobrenome é necessário', 'error')
        return
    }
    if (!email){
        genericSweetAlert("Error", 'Email é requerido', 'error')
        return
    }
    if (!password){
        genericSweetAlert("Error", 'Password é necessária', 'error')
        return
    }
    var sign_up_data = new FormData();
    // console.log(data);
    // return false;
    sign_up_data.append('first_name', first_name);
    sign_up_data.append('last_name', last_name);
    sign_up_data.append('email', email);
    sign_up_data.append('password', password);

    loadingSweetAlert(title = 'Por favor, espere');
    $.ajax({
        url: this.sign_up_url, // the endpoint
        type: "POST", // http method
        processData: false,
        contentType: false,
        data: sign_up_data,
        // data: $('#add-content-form').formSerialize(),
        dataType: "json",
        xhrFields: {
            withCredentials: true
        },

        success: function (json) {
            console.log(json)
            setCookie("u-at", json.payload.access_token, 100);
            saveToLocalStorage("u-at", json.payload.access_token)
            // simpleToastNotification("success", json.description)
            if (self.next){
                window.location.href = self.next;
            }else{
                window.location.href = self.home_url;
            }
        },
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("Authorization", "Token " + getCookie('u-at'));
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        },

        // handle a non-successful response
        error: function (xhr, errmsg, err) {
            data = xhr.responseJSON;
            genericSweetAlert(title = "Error", text=data.description, type = 'error');
        }
    });
}


SignUp.prototype.LoginUpFormSubmit = function () {
    var self = this;
    let email = $("#email").val();
    let password = $("#password").val();
    if (!email){
        genericSweetAlert("Error", 'Email é requerido', 'error')
        return
    }
    if (!password){
        genericSweetAlert("Error", 'Password é necessária', 'error')
        return
    }
    var login_up_data = new FormData();
    login_up_data.append('email', email);
    login_up_data.append('password', password);

    loadingSweetAlert(title = 'Por favor, espere');
    $.ajax({
        url: this.login_url, // the endpoint
        type: "POST", // http method
        processData: false,
        contentType: false,
        data: login_up_data,
        // data: $('#add-content-form').formSerialize(),
        dataType: "json",
        xhrFields: {
            withCredentials: true
        },

        success: function (json) {
            // console.log(json)
            setCookie("u-at", json.payload.access_token, 10000);
            saveToLocalStorage("u-at", json.payload.access_token);
            window.location.href = self.home_url;
        },
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("Authorization", "Token " + getCookie('u-at'));
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        },

        // handle a non-successful response
        error: function (xhr, errmsg, err) {
            data = xhr.responseJSON;
            genericSweetAlert(title = "Error", text=data.description, type = 'error');
        }
    });
}