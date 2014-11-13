$(function() {
    var graph;

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
    $.jqplot.config.enablePlugins = true;
    if(data.fields.passed === 0){
        s1 = [data.fields.a, data.fields.b, data.fields.c, data.fields.d, data.fields.e, data.fields.f]
        ticks = ['A', 'B', 'C', 'D', 'E', 'F'];
        colors = [ "#00CC00", "#00CC33", "#CCFF33", "#FFFF00", "#FF6600", "#CC0000"];
    }
    else{
        s1 = [data.fields.passed, data.fields.f]
        ticks = ['Bestått', 'Ikke bestått']
        colors = [ "#00CC00", "#CC0000"];
    }
    graph = $.jqplot('grades-graph', [s1],
    {
        seriesColors: colors,
        
        seriesDefaults:
        {
            renderer:$.jqplot.BarRenderer,
            pointLabels: { show: true, formatString: '%d', formatter: $.jqplot.DefaultTickFormatter},
            rendererOptions: { barMargin: 2, varyBarColor: true}
        },
        axes:
        {
            xaxis: 
            {
                renderer: $.jqplot.CategoryAxisRenderer,
                ticks: ticks,
                tickOptions: { showGridLine: false }
            },
            yaxis:
            {
                tickOptions: { show: false}
            }
        },
        grid:{ gridLineColor: '#FFF'}
    });
    }

    function createButtons(json){
        for(i = 0; i < json.length; i++){
            $("#grade-buttons").append("<button type=\"button\" id=" + i + " class=\"btn-grade btn btn-default\">" + json[i].fields.semester_code + "</button>");
        }

        $(".btn-grade").first().addClass("active");
        
        $(".btn-grade").bind('click', function(event){
            $(".btn-grade").removeClass("active");
            $(event.target).addClass("active");
            data = json[event.target.id];
            if(data.fields.passed === 0){
                s1 = [data.fields.a, data.fields.b, data.fields.c, data.fields.d, data.fields.e, data.fields.f];
            }
            else{
                s1 = [data.fields.passed, data.fields.f];
            }
            graph.replot({data:[s1]});
        });
    }
    
    

    $(document).ready(function()
    {
        $.getJSON("grades/", function(json)
        {
            createGraph(json[0]);
            createButtons(json);
        });
    });

});

