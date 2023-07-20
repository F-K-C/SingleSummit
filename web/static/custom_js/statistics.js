/**
 * Created by Ashar on 7/1/2020.
 */

let LIMIT = 10;
let OFFSET = 0;
let USER_ID = 0;
let CITY = '';
let TYPE = '';
let PIE_CHART = null;
let DOGHNUT_CHART = null;
let EVENT_BAR_CHART = null;
let PARTICIPANT_BAR_CHART = null;
let PRICE_CHART = null;
let GRADE_CHART = null;

Statistics = function (data) {
    this.stats_url = data.stats_url;
    this.loader = data.loader;
    const self = this;

    // self.event_data = $("#event-data");

    $("#city").on('change', function () {
        CITY = $(this).val()
        self.init_data(self.stats_url, self.create_url(CITY, TYPE));
    });
    $("#type").on('change', function () {
        TYPE = $(this).val()
        self.init_data(self.stats_url, self.create_url(CITY, TYPE));
    });
    // Init Events Data
    self.init_data(self.stats_url, self.create_url(CITY, TYPE));

};

Statistics.prototype.bar_chart = function (chart_id, chart_label = "Event", type="bar") {
    const labels = ["January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ];
    const data_set = {
        labels: labels,
        datasets: []
    };
    return new Chart($(`#${chart_id}`).get(0).getContext('2d') , {
        type: type,
        data: data_set,
        options: {
            scales: {
                yAxes: [{
                    ticks: {
                        beginAtZero: true
                    }
                }]
            }
        }
    })
}

Statistics.prototype.return_bar_data_set = function(event_data, chart_label = "Event", is_monthly = true){
    let labels = [];
    if(is_monthly){
        labels = ["January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ];
        // data_com = labels.map((i, index) => {
        //     return event_data.map(j => {
        //         val = j.data_name
        //         return index === val - 1 ? j.count : 0
        //     })
        // })
        data_com = []
        for (i=0; i<labels.length;i++){
            j_arr = 0;
            for (j=0; j<event_data.length;j++){
                if (i === event_data[j].data_name - 1){
                    j_arr = event_data[j].count
                }
            }
            data_com.push(j_arr)
        }
        console.log("Month", data_com);
    }else{
        labels = event_data.map(i => i.data_name);
        data_com = event_data.map(i => i.count)
    }
    let color_code = labels.map(i => generateHexCode());

    const data_set = {
        labels: labels,
        datasets: [{
            label: chart_label,
            data: data_com,
            backgroundColor: color_code.map(i => i + '36'),
            borderColor: color_code,
            borderWidth: 1
        }]
    };
    return data_set
}

Statistics.prototype.donut_chart = function (city_data, chart_id, type="doughnut") {
    var donutChartCanvas = $(`#${chart_id}`).get(0).getContext('2d')

    var donutData = {
        labels: [],
        datasets: []
    }
    var donutOptions = {
        maintainAspectRatio: false,
        responsive: true,
    }
    //Create pie or douhnut chart
    // You can switch between pie and douhnut using the method below.
    // Chart(donutChartCanvas).destroy();

    return new Chart(donutChartCanvas, {
        type: type,
        data: donutData,
        options: donutOptions
    })

}

Statistics.prototype.donut_data_return = function(city_data){
            return donutData = {
                labels: city_data.map(i => i.data_name),
                datasets: [
                    {
                        data: city_data.map(i => i.count),
                        backgroundColor: city_data.map(i => generateHexCode()),
                    }
                ]
            }
}

Statistics.prototype.init_data = function (url, query_parameter = "?", load_more = false) {
    const self = this;
    $.ajax({
        url: url + query_parameter, // the endpoint
        type: "GET", // http method
        headers: {},
        success: function (json) {
            // console.log(json.payload.event_data_grade);
            // var previousChart = Chart.instances[0];
            // console.log(previousChart);
            // // Step 2: Destroy the previous chart
            // if (previousChart) {
            //   previousChart.destroy();
            // }
            // self.destroy_chart("city_donut_chart")
            // self.destroy_chart("type_donut_chart")
            if (!DOGHNUT_CHART){
                DOGHNUT_CHART = self.donut_chart(json.payload.city_data, "city_donut_chart")
            }
            DOGHNUT_CHART.config.data = self.donut_data_return(json.payload.city_data);
            DOGHNUT_CHART.update();
            if (!PIE_CHART){
                PIE_CHART = self.donut_chart(json.payload.type_data, "type_donut_chart", "pie")
            }
            PIE_CHART.config.data = self.donut_data_return(json.payload.type_data);
            PIE_CHART.update();

            if(!EVENT_BAR_CHART){
                EVENT_BAR_CHART = self.bar_chart("event_bar_chart", "Event Chart");
            }
            console.log(self.return_bar_data_set(json.payload.event_data, "Event Chart"));
            EVENT_BAR_CHART.config.data = self.return_bar_data_set(json.payload.event_data, "Event Chart");
            EVENT_BAR_CHART.update()
            if(!PARTICIPANT_BAR_CHART){
                PARTICIPANT_BAR_CHART = self.bar_chart("event_participant_bar_chart", "Participant Chart");
            }
            PARTICIPANT_BAR_CHART.data = self.return_bar_data_set(json.payload.event_participant_data, "Participant Chart");
            PARTICIPANT_BAR_CHART.update()

            if(!GRADE_CHART){
                GRADE_CHART = self.bar_chart("event_participant_grade_chart", "Grade Chart");
            }
            GRADE_CHART.data = self.return_bar_data_set(json.payload.event_data_grade, "Grade Chart", false);
            GRADE_CHART.update()

            if(!PRICE_CHART){
                PRICE_CHART = self.bar_chart("event_price_chart", "Event Price Chart");
            }
            PRICE_CHART.data = self.return_bar_data_set(json.payload.event_price, "Event Price Chart", false);
            PRICE_CHART.update()


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

Statistics.prototype.create_url = function (city="", type="") {
    return `?city=${city}&type=${type}`;
}