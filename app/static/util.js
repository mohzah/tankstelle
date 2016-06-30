var options = {
    chart: {
        type: 'column',
        zoomType: 'y'
    },
    // data: {
    //     table: 'datatable'
    // },
    title: {
        text: 'Gas Prices'
    },
    subtitle: {
        text: 'Pinch to zoom in',
    },
    xAxis: {
        categories: ['E5', 'E10', 'Diesel'],
        crosshair: true,
        labels: {
            // rotation: -45,
            style: {
                fontSize: '16px',
                // fontFamily: 'Verdana, sans-serif'
            }
        }
    },
    yAxis: {
        title: {
            text: 'Price \u20AC'
        },
        tickInterval: 0.02,
        min: 0.8,
        labels: {
            formatter: function() {
                return '<title>' + this.value + ' \u20AC' + '</title>';
            }
        }
    },
    tooltip: {
        headerFormat: '<span style="font-size:13px; font-weight: bold;">{point.key}</span><table>',
        pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
        '<td style="padding:0"><b>{point.y:.3f} \u20AC</b></td></tr>',
        footerFormat: '</table>',
        shared: true,
        useHTML: true
    },
    // tooltip: {
    //     valueSuffix: ' \u20AC',
    //     shared: true,
    //     // formatter: function() {
    //     //     return  this.y +' \u20AC \n' + this.series.name  ;
    //     // }
    //     // formatter: function () {
    //     //     return '<b>' + this.series.name + '</b>' +
    //     //         this.y + ' ';
    //     // }
    // },
    legend: {
        layout: 'vertical',
        // enabled: false
    },
    dataLabels: {
        enabled: true,
        rotation: -90,
        color: '#FFFFFF',
        align: 'right',
        format: '{point.y:.1f}', // one decimal
        y: 10, // 10 pixels down from the top
        style: {
            fontSize: '13px',
            fontFamily: 'Verdana, sans-serif'
        }
    },
    series: []
};


var hourly_options = {
    chart: {
            type: 'line'
        },
        title: {
            text: 'Hourly Average Price'
        },
        xAxis: {
            title: {
                text: 'Time (hour)'
            },
            tickInterval: 1,
            min:0,
            max:23
        },
        yAxis: {
            title: {
                text: 'Price (\u20AC)'
            }
        },
        plotOptions: {
            line: {
                dataLabels: {
                    enabled: true
                },
                enableMouseTracking: true
            }
        },
        series: [{name:'E5',
                  data:[[12, 2],[13,4]]
                 }
                ]
};


function minimum(stations) {
    // find minimum diesel price in list to determine min of chart
    var min_price = stations[0]['data'][2];
    var len = stations.length;
    for (i = 1; i < len; i++) {
        diesel_price = stations[i]['data'][2]
        if (diesel_price < min_price) {
            min_price = diesel_price;
        }
    }
    return min_price;
}


function fillRow(rowId, station) {
    $(rowId+' td:nth-child(2)').text(station.name);
    $(rowId+' td:nth-child(3)').text(station.data[0] +' - '+ station.data[1]);
    $(rowId+' td:nth-child(4)').text(station.data[2]);
    // removing city name and post code from address string
    last_space = station.address.lastIndexOf(',');
    short_address = station.address.substring(0, last_space);
    cordination = station.lat + ',' + station.lng;
    
    link = '<a href="https://www.google.de/maps/dir//' + cordination +
            '/@' + cordination + ',16z">' +
            '<span class="glyphicon glyphicon-map-marker" aria-hidden="true"></span>' +
            short_address + '</a>';
    $(rowId+' td:nth-child(5)').html(link);
}


function geoplace(position) {
    lat = position.coords.latitude;
    lng = position.coords.longitude;
    $.ajax({
        type        : 'GET', // define the type of HTTP verb we want to use (POST for our form)
        url         : 'find?cord=' + lat +','+ lng, // the url where we want to POST
        dataType    : 'json', // what type of data do we expect back from the server
    }).done(presentData);
}


function presentData(data) {
    if (data.status === 'error') {
        $("#alert").text(data.error);
        $("#alert").show();
    }
    else {
        options.yAxis.min = 0.9 * minimum(data.stations);
        options.series = data.stations;
        $('#prices').highcharts(options);
        // here we will handle errors and validation messages
        $('#top-stations').show();
        fillRow("#cheapest-row", data.stations[0]);
        fillRow("#closest-row", data.closest);

        hourly_options.series = data.hourly;
        $('#hourly').highcharts(hourly_options);
    }
}


$(function () { 
    // Document is Ready
    $('#top-stations').hide();
    $("#alert").hide();
    $('#prices').hide();

    $('#contact').attr('href', 'mailto:gtankstel'+'le@gmail.com');

    if (navigator.geolocation) {
        // browswer support geolocation
        navigator.geolocation.getCurrentPosition(geoplace);
    }

    $('#plz-form').submit(function( event ) {
        $("#alert").hide();
        $('#notice').hide();
        $('#prices').show();

        var formData = {'query': $('#query').val()};
        $.ajax({
            type        : 'POST', // define the type of HTTP verb we want to use (POST for our form)
            url         : 'submit', // the url where we want to POST
            data        : formData, // our data object
            dataType    : 'json', // what type of data do we expect back from the server
            encode      : true
        })
            // using the done promise callback
            .done(presentData);

        event.preventDefault();

    }); 
});