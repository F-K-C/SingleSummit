/**
 * Created by Ashar on 7/1/2020.
 */

Dashboard = function (data) {
    this.event_url = data.event_url;
    const self = this;

    self.init_calendar();
    self.init_event_data();

};

Dashboard.prototype.init_event_data = function () {
    let self = this;
    $.ajax({
        url: `${self.event_url}?is_calendar=true`, // the endpoint
        type: "GET", // http method
        success: function (json) {
            data = json.payload;
            let event_arr = []
            data.map(i => {
                event_arr.push({
                    title: i.name,
                    url: `/event-detail/${i.id}`,
                    start: i.date,
                    end: i.date,
                    backgroundColor: generateHexCode()
                })
            });
            self.init_calendar(event_arr);
        },
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
            }
        },
        // handle a non-successful response
        error: error_function
    });
}


Dashboard.prototype.init_calendar = function (event_arr = []) {
    // let calander_height = $(document).height() - $("#header").height();
    // $("#calendar-container-2").css("height", calander_height - 40);

    let calendarEl = document.getElementById('calendar');

    let calendar = new FullCalendar.Calendar(calendarEl, {
        lang: 'es',
        height: '100%',
        expandRows: true,
        slotMinTime: '00:00',
        slotMaxTime: '23:00',
        buttonText:{
          today:    'hoje',
          month:    'Mês',
          week:     'Semana',
          day:      'Dia',
          list:     'Lista'
        },
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay,listWeek'
        },
        initialView: 'dayGridMonth',
        initialDate: get_or_convert_date_to_system_time_zone(),
        navLinks: true, // can click day/week names to navigate views
        editable: true,
        selectable: true,
        nowIndicator: true,
        dayMaxEvents: true, // allow "more" link when too many events
        events: event_arr,
        eventClick: function (info) {
            // alert('Event: ' + info.event.title);
            // alert('Coordinates: ' + info.jsEvent.pageX + ',' + info.jsEvent.pageY);
            //
            // // change the border color just for fun
            // info.el.style.borderColor = 'red';
            info.jsEvent.preventDefault(); // don't let the browser navigate

            if (info.event.url) {
                window.open(info.event.url);
            }
        }
    });

    calendar.render();
}


Dashboard.prototype.create_url = function (selection) {
    return '?type=' + selection;
}