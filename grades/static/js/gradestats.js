$(function() {
    var graph;

    function createGraph(data){
        $.jqplot.config.enablePlugins = true;
        var s1, ticks, colors;
        if(data.passed === 0){
            s1 = [data.a, data.b, data.c, data.d, data.e, data.f]
            ticks = ['A', 'B', 'C', 'D', 'E', 'F'];
            colors = [ "#00CC00", "#00CC33", "#CCFF33", "#FFFF00", "#FF6600", "#CC0000"];
            barMargin = 2;
            max = null;
        }
        else{
            s1 = [data.passed, data.f]
            ticks = ['Bestått', 'Ikke bestått']
            colors = [ "#00CC00", "#CC0000"];
            barMargin = 10;
            max = ((data.passed == data.f) ? data.passed +1 : null);
        }
        graph = $.jqplot('grades-graph', [s1],
        {
            seriesColors: colors,

            seriesDefaults:
            {
                renderer:$.jqplot.BarRenderer,
                pointLabels: { show: true, formatString: '%d', formatter: $.jqplot.DefaultTickFormatter},
                rendererOptions: { barMargin: barMargin, varyBarColor: true}
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
                    max: max,
                    tickOptions: { show: false}
                }
            },
            grid:{ gridLineColor: '#FFF'}
        });
    }

    function createButtons(json){
        if($("#grade-buttons").innerWidth() < 320){
            var breakPoint = 3;
        }
        else{
            var breakPoint = 4;
        }

        var buttonGroup = document.createElement('div');

        $(buttonGroup).addClass("btn-group");

        for(var i = 0; i < json.length; i++){
            if(i % breakPoint == 0 && i != 0){
                $("#grade-buttons").append(buttonGroup);
                buttonGroup = document.createElement('div');
                $(buttonGroup).addClass("btn-group");
            }
            $(buttonGroup).append("<button type=\"button\" id=\"" + i + "\" class=\"btn-grade btn btn-default\">" + json[i].semester_code + "</button>");
        }
        
        $("#grade-buttons").append(buttonGroup);
        $("#average-grade").text(json[0].average_grade.toFixed(2));
        $(".btn-grade").last().addClass("active");
        
        $(".btn-grade").bind('click', function(event){
            var data, s1;
            $(".btn-grade").removeClass("active");
            $(event.target).addClass("active");
            data = json[event.target.id];

            $("#average-grade").text(data.average_grade.toFixed(2));

            graph.destroy();
            createGraph(data);
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
                createGraph(json[json.length - 1])
            },
            error: function(e) {
                console.log(e.message);
            }
        });
    });

});

