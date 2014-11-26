$(function() {
    var graph;

    function createGraph(data){
        $.jqplot.config.enablePlugins = true;
        var s1, ticks, colors;
        if(data.passed === 0){
            s1 = [data.a, data.b, data.c, data.d, data.e, data.f]
            ticks = ['A', 'B', 'C', 'D', 'E', 'F'];
            colors = [ "#00CC00", "#00CC33", "#CCFF33", "#FFFF00", "#FF6600", "#CC0000"];
        }
        else{
            s1 = [data.passed, data.f]
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
        var buttonGroup = document.createElement('div');
        $(buttonGroup).addClass("btn-group");

        for(var i = 0; i < json.length; i++){
            if(i % 4 == 0 && i != 0){
                $("#grade-buttons").append(buttonGroup);
                buttonGroup = document.createElement('div');
                $(buttonGroup).addClass("btn-group");
            }
            $(buttonGroup).append("<button type=\"button\" id=\"" + i + "\" class=\"btn-grade btn btn-default\">" + json[i].semester_code + "</button>");
        }
        
        $("#grade-buttons").append(buttonGroup);

        $("#average-grade").text(json[0].average_grade.toFixed(2));

        $(".btn-grade").first().addClass("active");
        
        $(".btn-grade").bind('click', function(event){
            var data, s1;
            $(".btn-grade").removeClass("active");
            $(event.target).addClass("active");
            data = json[event.target.id];

            $("#average-grade").text(data.average_grade.toFixed(2));

            if(data.passed === 0){
                s1 = [data.a, data.b, data.c, data.d, data.e, data.f];
            }
            else{
                s1 = [data.passed, data.f];
            }
            graph.replot({data:[s1]});
        });
    }

    $(document).ready(function()
    {
        $.ajax({
            type: 'GET',
            url: "grades/",
            async: false,
            jsonpCallback: 'parse',
            contentType: "application/json",
            dataType: 'jsonp',
            success: function(json) {
                createButtons(json)
                createGraph(json[0])
            },
            error: function(e) {
                console.log(e.message);
            }
        });
    });

});

