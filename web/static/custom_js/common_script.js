function simpleToastNotification(type = "success", message = "") {
    $.simplyToast(type, message, {
        offset:
            {
                from: "bottom",
                amount: 10
            },
        align: "right",
        width: 300,
        delay: 2500,
        allow_dismiss: false,
        stackup_spacing: 10
    });
}

function getCookie(cname) {
    let name = cname + "=";
    let decodedCookie = decodeURIComponent(document.cookie);
    let ca = decodedCookie.split(';');
    for (let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}

function setCookie(cname, cvalue, exdays) {
    const d = new Date();
    d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000));
    let expires = "expires=" + d.toUTCString();
    document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}

const error_function = function (xhr, errmsg, err) {
    if (xhr.status === 403 || xhr.status === 401) {
        data = xhr.responseJSON;
        message = "detail" in data ? data.detail : data.description
        genericSweetAlert(title = "Error", text = message, type = 'error').then(function () {
            window.location.href = "/";
        });

    } else if (xhr.status === 500) {
        genericSweetAlert(title = "Error", text = xhr.statusText, type = 'error');

    } else if (xhr.status === 404) {
        genericSweetAlert(title = "Error", text = xhr.statusText, type = 'error');

    } else if (xhr.status === 422) {
        genericSweetAlert(title = "Error", text = xhr.responseJSON.description, type = 'error');

    }
}

$("#logout").on("click", function (e) {
    e.preventDefault();
    $.ajax({
        url: "/api/user/logout", // the endpoint
        type: "GET", // http method
        headers: {},
        success: function (json) {
            if (json['success'] == true) {
                setCookie("u-at", "")
                saveToLocalStorage("u-at", "")
                window.location.href = "/"
            }
        },
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
            }
            xhr.setRequestHeader("Authorization", "Bearer " + getCookie('u-at'));
        },
        // handle a non-successful response
        error: function (xhr, errmsg, err) {
            if (xhr.status == 403) {
                genericSweetAlert(title = "Error", type = 'error');
            }
            console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
        }
    });
})


function convertToSlug(Text) {
    return Text.toLowerCase()
        .replace(/ /g, '-')
        .replace(/[^\w-]+/g, '');
}

function get_or_convert_date_time_to_system_time_zone(date = "") {
    let time_zone = Intl.DateTimeFormat().resolvedOptions().timeZone;
    if (date) {
        return new Date(date).toLocaleString("en-US", {timeZone: time_zone})
    }
    return new Date().toLocaleString("en-US", {timeZone: time_zone})
}

function get_or_convert_date_to_system_time_zone(date = "") {
    let time_zone = Intl.DateTimeFormat().resolvedOptions().timeZone;
    if (date) {
        return new Date(date).toISOString().split('T')[0].toLocaleString("en-US", {timeZone: time_zone})
    }
    return new Date().toISOString().split('T')[0].toLocaleString("en-US", {timeZone: time_zone})
}


function generateHexCode() {
  const letters = '0123456789ABCDEF';
  let hexCode = '#';

  for (let i = 0; i < 6; i++) {
    hexCode += letters[Math.floor(Math.random() * 16)];
  }

  return hexCode;
}


function get_date_time_to_human_readable(date){
    const now = new Date(date); // Get the current date and time

    const year = now.getFullYear(); // Get the year (e.g., 2023)
    const month = now.toLocaleString('default', { month: 'long' }); // Get the full month name (e.g., July)
    const day = now.getDate(); // Get the day of the month (e.g., 9)
    const time = now.toLocaleString('en-US', { hour: 'numeric', minute: 'numeric', hour12: true });

    const formattedDateTime = `${month} ${day}, ${year} ${time}`; // Assemble the formatted string
    return formattedDateTime
}


function SOCKET(path) {
    // let port = ":8001";
    let port = "";
    let wsStart = "";
    if (window.location.protocol == 'https:') {
        wsStart = 'wss://';
    } else if (window.location.protocol == 'http:') {
        wsStart = 'ws://';
    }
    let endpoint = wsStart + window.location.host + port + path;
    let socket = new WebSocket(endpoint)

    return socket;
}


function formatDatetime(datetime) {
    var currentDatetime = new Date(); // Current datetime
    datetime = new Date(datetime);
    var dayDifference = Math.abs(datetime.getDate() - currentDatetime.getDate()); // Calculate the day difference

    if (dayDifference < 7) {
        // Display day string if the day difference is exactly 7
        var dayString = datetime.toLocaleDateString(undefined, {weekday: 'short'});
        var timeOptions = {hour: 'numeric', minute: 'numeric'};
        var formattedTime = datetime.toLocaleTimeString(undefined, timeOptions);
        // console.log(dayString)
        return dayString + ' ' + formattedTime;
    } else {
        // Display date/day and time for other cases
        var dateOptions = {month: '2-digit', day: '2-digit'};
        var timeOptions = {hour: 'numeric', minute: 'numeric'};

        var formattedDate = datetime.toLocaleDateString(undefined, dateOptions);
        var formattedTime = datetime.toLocaleTimeString(undefined, timeOptions);
        return formattedDate + ' ' + formattedTime;
    }
}