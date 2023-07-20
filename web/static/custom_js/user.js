/**
 * Created by Ashar on 7/1/2020.
 */

User = function (data) {
    this.users_datatable_url = data.users_datatable_url;
    this.users_status_url = data.users_status_url;
    this.users_delete_url = data.users_delete_url;
    this.users_url = data.users_url;
    this.user_datatable = null;
    const self = this;

    self.user_datatable = $("#user-datatable");
    self.init_data_table();

    self.user_datatable.on('click', '.status-user', function () {
        self.change_status(self.users_status_url, $(this).attr("data-pk"));
    });

    self.user_datatable.on('click', '.delete-user', function () {
        self.change_status(self.users_delete_url, $(this).attr("data-pk"));
    });

    $("#submit").on('click', function () {
        self.user_data_submit(self.users_url);
    });

    $("#add-user").on('click', function(){
       $("#create-user-modal").modal('show');
       let edit = $("#edit");
        edit.addClass("d-none");
        $("#submit").removeClass("d-none");
                        $("#user-create").trigger("reset");
                $("#password").parent().removeClass('d-none')
    });

    self.user_datatable.on('click', '.edit-user', function () {
        let data = JSON.parse(decodeURI($(this).attr("data-pk")));
        $("#user-create").trigger("reset");
        $("#create-user-modal").modal('show');
        $("#first_name").val(data.first_name);
        $("#last_name").val(data.last_name);
        $("#email").val(data.email);
        $("#password").parent().addClass('d-none');
        let edit = $("#edit");
        edit.removeAttr("data-pk");
        $("#submit").addClass("d-none");
        edit.removeClass("d-none");
        edit.attr("data-pk", data.id);
    });

    $("#edit").on("click", function(){
       let id = $(this).attr("data-pk");
       self.user_data_submit(self.users_url+id, "PUT");
    });


};


User.prototype.user_data_submit = function (url, type = 'POST') {
    var self = this;
    let first_name = $("#first_name").val();
    let last_name = $("#last_name").val();
    let email = $("#email").val();
    let password = $("#password").val();
    if(!first_name){
        genericSweetAlert("Error", "primeiro nome é necessário", 'error')
        return
    }
    if(!last_name){
        genericSweetAlert("Error", "Sobrenome é necessário", 'error')
        return
    }
    if(!email){
        genericSweetAlert("Error", "Email é requerido", 'error')
        return
    }

    var sign_up_data = new FormData();
    sign_up_data.append('first_name', first_name);
    sign_up_data.append('last_name', last_name);
    sign_up_data.append('email', email);
    if (type === 'POST'){
        if(!password){
            genericSweetAlert("Error", "Password é necessária", 'error')
            return
        }
        sign_up_data.append('password', password);
    }

    loadingSweetAlert(title = 'Por favor, espere');
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
            if (type === 'PUT'){
                $("#user-create").trigger("reset");
                $("#password").parent().removeClass('d-none')
                let edit = $("#edit");
                edit.addClass("d-none");
                $("#submit").removeClass("d-none");
            }
            if (json['success'] == true) {
                $("#create-user-modal").modal('hide');
                genericSweetAlert(title = 'Sucesso', text = json['description'], type = 'success').then((function () {
                    self.user_datatable.ajax.reload(null, false);
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


User.prototype.init_data_table = function (query_params = "?") {
    const self = this;
    self.user_datatable = $('#user-datatable').DataTable({
        "processing": true,
        "serverSide": true,
        "destroy": true,
        "ajax": {
            "url": self.users_datatable_url + query_params,
            "type": "GET",
            // dataSrc:"",
            // "dataSrc": "data.payload",

            headers: {
                "Authorization": "Bearer " + getCookie('u-at')
            },
            dataFilter: function (responsce) {
                var json = jQuery.parseJSON(responsce);
                json = json.payload
                totalEntries = json.recordsTotal;
                return JSON.stringify(json); // return JSON string
            },

            // handle a non-successful response
            error: error_function

        },
        "columns": [
            {
                "title": "ID",
                "data": "id",
                "mRender": function (data, type, full) {
                    if (data) {
                        return '<td>' + data + '</td>';
                    } else return '<td class="center"> - </td>'
                }
            },
            {
                "title": "nome",
                "data": "first_name",
                "mRender": function (data, type, full) {
                    if (data) {
                        return '<td><span class="">' + data + '</span></td>';
                    } else return '<td class="center"> - </td>'
                }
            },
            {
                "title": "Sobrenome",
                "data": "last_name",
                "mRender": function (data, type, full) {
                    if (data) {
                        return '<td><span class="">' + data + '</span></td>';
                    } else return '<td class="center"> - </td>'
                }
            },
            //             {
            //     "title": "Title",
            //     "data": "title",
            //     "mRender": function (data, type, full) {
            //         if (data) {
            //             return '<td><span class="text-uppercase">'+data+'</span></td>';
            //         } else return '<td class="center"> - </td>'
            //     }
            // },
            {
                "title": "Email",
                "data": "email",
                "mRender": function (data, type, full) {
                    if (data) {
                        return '<td>' + data + '</td>';
                    } else return '<td class="center"> - </td>'
                }
            },
                        {
                "title": "Events",
                "data": "events",
                "mRender": function (data, type, full) {
                    if (data) {
                        return '<td>' + data + '</td>';
                    } else return '<td class="center"> - </td>'
                }
            },

            {
                "title": "Is Active",
                "data": "is_active",
                "mRender": function (data, type, full) {
                    if (data) {
                        return '<td><span class="text-success">Active</span></td>';
                    } else return '<td class="center"> <span class="text-danger">InActive</span></td>'
                }
            },
            {
                "title": "Actions",
                'data': 'id',
                "mRender": function (data, type, full) {

                    if (data) {
                        let operations = '';
                        if (full.is_active) {
                            operations += '<a title="Enable" data-pk="' + full.id + '" style="padding-right: 1px;  cursor: pointer"  class="on-default remove-row status-user"><i class="fa fa-ban text-danger"></i> </a>';
                        } else {
                            operations += '<a title="Disable" data-pk="' + full.id + '" style="padding-right: 1px; cursor: pointer"  class="on-default remove-row status-user"><i class="fa fa-check text-success"></i> </a>';
                        }
                        let stringify_data = encodeURI(JSON.stringify(full));
                        operations += '<a title="Delete" data-pk="' + full.id + '" style="padding-right: 1px; cursor: pointer"  class="delete-user"><i class="fa fa-trash text-danger"></i></a>';
                        operations += `<a title='Edit' data-pk='${stringify_data}' style='padding-right: 2px; cursor: pointer'  class='edit-user'><i class="fa fa-pencil-alt text-info"></i></a>`;
                        return operations;

                    }
                }

            }

        ],

    });
};


User.prototype.change_status = function (url, id) {
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
                    self.user_datatable.ajax.reload(null, false);
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


User.prototype.create_url = function (selection) {
    return '?type=' + selection;
}