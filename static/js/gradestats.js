$(function() {
    /* AJAX SETUP FOR CSRF */
    $.ajaxSetup({
        crossDomain: false, // obviates need for sameOrigin test
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", $.cookie('csrftoken'));
            }
        }
    });
    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    /* END AJAX SETUP */

    function createGraph(data){
    data = grades[0];
    $.jqplot.config.enablePlugins = true;
    var s1 = [data.fields.a, data.fields.b, data.fields.c, data.fields.d, data.fields.e, data.fields.f]
    var ticks = ['A', 'B', 'C', 'D', 'E', 'F'];
    graph = $.jqplot('grades-graph', [s1],
    {
        seriesColors: [ "#00CC00", "#00CC33", "#CCFF33", "#FFFF00", "#FF6600", "#CC0000"],
        
        seriesDefaults:
        {
            renderer:$.jqplot.BarRenderer,
            pointLabels: { show: true },
            rendererOptions: { barMargin: 2, varyBarColor: true},
        },
        axes:
        {
            xaxis: 
            {
                renderer: $.jqplot.CategoryAxisRenderer,
                ticks: ticks,
                tickOptions: { showGridLine: false },
            },
            yaxis:
            {
                tickOptions: { show: false}
            }
        },
        grid:{ gridLineColor: '#FFF',}
    });
   

    $(document).ready(function()
    {
        $.getJSON("grades/", function(json)
        {
            print(json);
        });
    });

});

