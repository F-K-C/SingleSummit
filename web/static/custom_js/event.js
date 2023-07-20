/**
 * Created by Ashar on 7/1/2020.
 */

let LIMIT = 10;
let OFFSET = 0;
let EVENT_DATA_TYPE = 0;
let EMAIL_LIST = [];
// 0 => all
// 1 => participated
// 2 => my events

Events = function (data) {
    this.event_delete_url = data.event_delete_url;
    this.event_url = data.event_url;
    this.event_data = null;
    this.user_id = data.user_id;
    this.event_join_url = data.event_join_url;
    this.event_detail_bool = data.event_detail_bool;
    this.user_role = data.user_role;
    this.event_invitation_url = data.event_invitation_url;
    this.loader = data.loader;
    const self = this;


    // Init Events Data
    if (!self.event_detail_bool) {
        self.init_data(self.event_url, self.create_url(LIMIT, OFFSET, EVENT_DATA_TYPE));
        self.event_data = $("#event-data");
    } else {
        self.event_data = $("#detail-id");

    }

    $('#email-list').tagList('create', {
        tagValidator: function (emailid) {
            // @warning: not sure if this RegExp is good enough for all types of email ids
            var emailPat = /^[A-Za-z]+[A-Za-z0-9._]*@[A-Za-z0-9]+\.[A-Za-z.]*[A-Za-z]+$/;
            return emailPat.test($.trim(emailid));
        }
    });

    $( '#email-list' ).on( 'tagadd', function( $event, tagText, opStatus, message ) {
      if( opStatus === 'success' ) {
        console.log( 'Email \'' + tagText + '\' added' );
        EMAIL_LIST.push(tagText);
      } else if( opStatus === 'failure' ) {
        genericSweetAlert("Error",'Email \'' + tagText + '\' could not be added.Please add a valid email', 'error' );
      }
    });

    $( '#email-list' ).on( 'tagremove', function( $event, tagText ) {
        EMAIL_LIST = EMAIL_LIST.filter(e => e !== tagText)
      console.log( 'Tag \'' + tagText + '\' removed' );
    });

    self.event_data.on('click', ".share-event", function(){
       $("#share-event-modal").modal('show');
       $("#invite-submit").attr("data-pk",$(this).attr("data-pk"))
    });

    $("#invite-submit").on('click', function(){
        if(EMAIL_LIST.length === 0){
            genericSweetAlert("Error", "Ao menos um email é necessário", "error")
            return
        }
        var sign_up_data = new FormData();
        sign_up_data.append('email_list', EMAIL_LIST);
        sign_up_data.append('id', $(this).attr('data-pk'));
        loadingSweetAlert("Por favor, espere");
        $.ajax({
        url: self.event_invitation_url, // the endpoint
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
            if (json['success'] == true) {
                $("#share-event-modal").modal('hide');
                EMAIL_LIST = [];
                $('#email-list').tagList('create', {
                    tagValidator: function (emailid) {
                        // @warning: not sure if this RegExp is good enough for all types of email ids
                        var emailPat = /^[A-Za-z]+[A-Za-z0-9._]*@[A-Za-z0-9]+\.[A-Za-z.]*[A-Za-z]+$/;
                        return emailPat.test($.trim(emailid));
                    }
                });

                genericSweetAlert(title = 'Sucesso', text = json['description'], type = 'success');
            }
        },
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("Authorization", "Token " + getCookie('u-at'));
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        },

        // handle a non-successful response
        error: error_function
    });
    });

    $("#add-event").on('click', function () {
        $("#create-event-modal").modal('show');
        $("#event-create").trigger("reset");
        let edit = $("#edit");
        edit.addClass("d-none");
        $("#submit").removeClass("d-none");
    });
    // Select All Events
    $("#all-events").on('click', function () {
        EVENT_DATA_TYPE = 0;
        LIMIT = 10;
        OFFSET = 0;
        $(this).parent().find('.btn-primary').removeClass('btn-primary').addClass('btn-outline-primary');
        $(this).removeClass('btn-outline-primary').addClass('btn-primary');
        self.init_data(self.event_url, self.create_url(LIMIT, OFFSET, EVENT_DATA_TYPE));
    });

    // Select My events
    $("#my-events").on('click', function () {
        EVENT_DATA_TYPE = 2;
        LIMIT = 10;
        OFFSET = 0;
        $(this).parent().find('.btn-primary').removeClass('btn-primary').addClass('btn-outline-primary');
        $(this).removeClass('btn-outline-primary').addClass('btn-primary');
        self.init_data(self.event_url, self.create_url(LIMIT, OFFSET, EVENT_DATA_TYPE));
    });

    // Participated My events
    $("#participated-events").on('click', function () {
        EVENT_DATA_TYPE = 1;
        LIMIT = 10;
        OFFSET = 0;
        $(this).parent().find('.btn-primary').removeClass('btn-primary').addClass('btn-outline-primary');
        $(this).removeClass('btn-outline-primary').addClass('btn-primary');
        self.init_data(self.event_url, self.create_url(LIMIT, OFFSET, EVENT_DATA_TYPE));
    });

    self.event_data.on('click', '.start', function () {
        let id = $(this).attr("data-pk");
        let value = $(this).attr("data-value");
        self.rate_event(id, value)
    });

    // Delete Event
    self.event_data.on('click', '.delete-event', function () {
        Swal.fire({
            title: 'Você gostaria de deletar esse evento?',
            text: "Todos os dados relacionados a esse evento serão deletados permanentemente",
            showCancelButton: true,
            confirmButtonText: 'Delete',
            confirmButtonColor: "red"
        }).then((result) => {
            /* Read more about isConfirmed, isDenied below */
            if (result.value) {
                self.change_status(self.event_delete_url, $(this).attr("data-pk"));
            }
        })
    });

    // Submit Event Creation
    $("#submit").on('click', function () {
        self.event_data_submit(self.event_url);
    });

    // Edit event pop-up
    self.event_data.on('click', '.edit-event', function () {
        let data = JSON.parse(decodeURIComponent($(this).attr("data-pk")));
        $("#event-create").trigger("reset");
        $("#create-event-modal").modal('show');
        // Append Data
        $("#name").val(data.name);
        $("#type").val(data.type);
        $("#local").val(data.local);
        $("#city").val(data.city);
        $("#date").val(new Date(data.date).toISOString().slice(0, 16));
        $("#price").val(data.price);
        $("#description").val(data.description);

        let edit = $("#edit");
        $("#password").parent().addClass('d-none');
        edit.removeAttr("data-pk");
        $("#submit").addClass("d-none");
        edit.removeClass("d-none");
        edit.attr("data-pk", data.id);
    });

    self.event_data.on('click', '.join-event', function () {
        let data = $(this).attr("data-pk");
        self.join_event(data)
    });

    // Edit Data Submit
    $("#edit").on("click", function () {
        let id = $(this).attr("data-pk");
        self.event_data_submit(self.event_url + id, "PUT");
    });

    // Load More
    self.event_data.on('click', '.load-more', function () {
        OFFSET = LIMIT + OFFSET;
        self.init_data(self.event_url, self.create_url(LIMIT, OFFSET, EVENT_DATA_TYPE), true);
    });
};


Events.prototype.event_data_submit = function (url, type = 'POST') {
    let self = this;
    let name = $("#name").val();
    let local = $("#local").val();
    let type_val = $("#type").val();
    let city = $("#city").val();
    let price = $("#price").val();
    let date = $("#date").val();
    let description = $("#description").val();
    if (!name) {
        genericSweetAlert("Error", "Name is required", 'error')
        return
    }
    if (!local) {
        genericSweetAlert("Error", "Local is required", 'error')
        return
    }
    if (!type_val) {
        genericSweetAlert("Error", "Type is required", 'error')
        return
    }
    if (!city) {
        genericSweetAlert("Error", "City is required", 'error')
        return
    }
    if (price < 0 || !price) {
        genericSweetAlert("Error", "Price is required", 'error')
        return
    }
    if (!date) {
        genericSweetAlert("Error", "Date is required", 'error')
        return
    }
    if (!description) {
        genericSweetAlert("Error", "Description is required", 'error')
        return
    }
    var sign_up_data = new FormData();
    sign_up_data.append('name', name);
    sign_up_data.append('local', local);
    sign_up_data.append('type', type_val);
    sign_up_data.append('city', city);
    sign_up_data.append('price', price);
    sign_up_data.append('date', date);
    sign_up_data.append('description', description);

    // loadingSweetAlert(title = 'Please wait');
    $.ajax({
        url: url, // the endpoint
        type: type, // http method
        processData: false,
        contentType: false,
        data: sign_up_data,
        // data: $('#add-content-form').formSerialize(),
        dataType: "json",
        xhrFields: {
            withCredentials: true
        },

        success: function (json) {
            if (type === "PUT") {
                $("#event-create").trigger("reset");
                let edit = $("#edit");
                edit.addClass("d-none");
                $("#submit").removeClass("d-none");
            }

            if (json['success'] == true) {
                $("#create-event-modal").modal('hide');
                genericSweetAlert(title = 'Sucesso', text = json['description'], type = 'success').then((function () {
                    if (!self.event_detail_bool) {
                        self.init_data(self.event_url, self.create_url(LIMIT, OFFSET, EVENT_DATA_TYPE));
                    } else {
                        location.reload()
                    }
                }));
            }
        },
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("Authorization", "Token " + getCookie('u-at'));
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        },

        // handle a non-successful response
        error: error_function
    });
}

Events.prototype.init_data = function (url, query_parameter = "?", load_more_flag = false) {
    const self = this;

    $("#event-data").append(`<div class="text-center gif-loader w-100"><img src="${self.loader}" /></div`);
    $.ajax({
        url: url + query_parameter, // the endpoint
        type: "GET", // http method
        headers: {},
        success: function (json) {
            let template = ``;
            if (json.count) {
                json.payload.map(i => {
                    template += self.append_event_data_template(i, self.user_id === i.user);
                });
            } else {
                template += `<div class="text-center no-event w-100 my-5">Nenhum evento encontrado</div>`
                $("#event-data").html(template);
                return;
            }
            let load_more = `<div class="text-center w-100 load-more-div"><button class="btn btn-outline-primary load-more" data-offset="${OFFSET}">Load More</button></div>`
            $(".gif-loader").remove();
            $(".no-event").remove();
            if (!load_more_flag) {
                $("#event-data").html(template + load_more);
            } else {
                $(".load-more-div").remove();
                $("#event-data").append(template + load_more);
            }
        },
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
            }
        },
        // handle a non-successful response
        error: error_function
    });
};

Events.prototype.append_event_data_template = function (i, creator = false) {
    let self = this;
    let buttons = `<a href="/event-detail/${i.id}" target="_blank" class="btn btn-warning mx-1 my-auto"><i
                            class="fa fa-eye"></i></a>`;
    let has_joined = i.participants.includes(self.user_id)
    let slugify = encodeURI(JSON.stringify(i));
    if (creator) {
        buttons += `<button data-pk="${slugify}" class="btn btn-info mx-1 edit-event"><i
                            class="fa fa-pencil-alt"></i></button>
                    <button data-pk="${i.id}" class="btn btn-danger mx-1 delete-event"><i
                            class="fa fa-trash"></i></button>`;
    } else {
        if (EVENT_DATA_TYPE === 1 && self.user_role != 'super-admin') {
            if (i.grade) {
                buttons += `<button class="btn btn-warning">${i.grade} <i class="fa fa-star"></i></button>`
            } else {
                buttons += `<div class="rate">
                            <input type="radio" id="star5" name="rate" value="5" />
                            <label for="star5" title="star5" data-pk="${i.id}" class="start" data-value="5">5 stars</label>
                             <input type="radio" id="star4" name="rate" value="4" />
                            <label for="star4" title="star4" data-pk="${i.id}" class="start" data-value="4">4 stars</label>
                            <input type="radio" id="star3" name="rate" value="3" />
                            <label for="star3" title="star3" data-pk="${i.id}" class="start" data-value="3">3 stars</label>
                            <input type="radio" id="star2" name="rate" value="2" />
                            <label for="star2" title="star2" data-pk="${i.id}" class="start" data-value="2">2 stars</label>
                            <input type="radio" id="star1" name="rate" value="1" />
                            <label for="star1" title="star1" data-pk="${i.id}" class="start" data-value="1">1 star</label>
                          </div>`;
            }
        } else {
            if (self.user_role != 'super-admin') {
                buttons += `<button title="Join Event" data-pk="${i.id}" class="btn ${has_joined ? "btn-outline-primary" : "btn-primary"} join-event">${has_joined ? "participando" : "Participar do evento"}</button>`;

            }
        }
    }
    if (EVENT_DATA_TYPE !== 1){
    buttons += `<a href="javascript:void(0)" data-pk="${i.id}" class="btn btn-info mx-1 my-auto share-event"><i
                            class="fa fa-share"></i></a>`;

    }

    return `<div class="card card-body d-flex p-3 my-3 mx-1 event justify-content-between flex-row overflow-hidden flex-wrap">
                <div class="d-flex flex-column justify-content-center my-auto date-time-design py-5 event-date">
                    <span>${new Date(i.date).getDate()}</span><span>${new Date(i.date).toLocaleString('default', {month: 'short'})}</span>
                </div>
                <div class="d-flex flex-column event-meta-data">
                    <div class="d-flex flex-column">
                        <div class="d-flex flex-row justify-content-between small-alert">
                            <div class="my-auto type text-center">${i.type}</div>
                            <div class="my-auto" style="font-size: 1.5rem">$ ${i.price}</div>
                        </div>
                        <h4>${i.name}</h4>
                        <div class="text-gray description">${i.description}</div>
                        <div><i class="fa fa-calendar mr-2"></i> ${get_date_time_to_human_readable(i.date)}</div>
                        <div><i class="fa fa-map-marker mr-2"></i>${i.local}, ${i.city}</div>
                        <div><i class="fa fa-users mr-2"></i>${i.participants.length}</div>
                        <div><i class=""><b>Organizador:</b> ${self.user_id === i.user? "You": i.first_name + ' '+i.last_name}</i></div>
                    </div>
                    <div class="d-flex flex-row justify-content-end my-2 small-alert">
                        ${buttons}
                    </div>
                </div>
            </div>`;
}

Events.prototype.change_status = function (url, id) {
    const self = this;
    loadingSweetAlert(title = 'Por favor, espere');
    $.ajax({
        url: url + "/" + id, // the endpoint
        type: "GET", // http method
        headers: {},
        success: function (json) {
            // console.log(json['success'])
            if (json['success'] == true) {
                genericSweetAlert(title = 'Sucesso', text = json['description'], type = 'success').then((function () {
                    if (!self.event_detail_bool) {
                        self.init_data(self.event_url, self.create_url(LIMIT, OFFSET, USER_ID));

                    } else {
                        window.location.href = "/event"
                    }
                }));
            }
        },
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
            }
        },
        // handle a non-successful response
        error: error_function
    });
};

Events.prototype.join_event = function (event_id) {
    const self = this;
    loadingSweetAlert(title = 'Por favor, espere');
    $.ajax({
        url: `/api/event/${event_id}/join_event/${self.user_id}`, // the endpoint
        type: "GET", // http method
        headers: {},
        success: function (json) {
            // console.log(json['success'])
            if (json['success'] == true) {
                genericSweetAlert(title = 'Sucesso', text = json['description'], type = 'success').then((function () {
                    if (!self.event_detail_bool) {
                        self.init_data(self.event_url, self.create_url(LIMIT, OFFSET, EVENT_DATA_TYPE));

                    } else {
                        location.reload()
                    }
                }));
            }
        },
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
            }
        },
        // handle a non-successful response
        error: error_function
    });
};

Events.prototype.rate_event = function (event_id, rating) {
    const self = this;
    loadingSweetAlert(title = 'Por favor, espere');
    $.ajax({
        url: `api/event/${event_id}/rate-event/${rating}`, // the endpoint
        type: "GET", // http method
        headers: {},
        success: function (json) {
            // console.log(json['success'])
            if (json['success'] == true) {
                genericSweetAlert(title = 'Sucesso', text = json['description'], type = 'success').then((function () {
                    if (!self.event_detail_bool) {

                        self.init_data(self.event_url, self.create_url(LIMIT, OFFSET, EVENT_DATA_TYPE));
                    } else {
                        location.reload()
                    }
                }));
            }
        },
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
            }
        },
        // handle a non-successful response
        error: error_function
    });
};

Events.prototype.create_url = function (limit = 10, offset = 0, event_data_type = 0) {
    return `?limit=${limit}&offset=${offset}&event_data_type=${event_data_type}`;
}