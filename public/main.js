/**
 * Created by rulkens on 03/04/15.
 */
$(document).ready(function(){

    var eos = new Eos();

    $('#stepSlider').slider().on('slide', function(e){
        eos.api('only', [e.value, 1]);
    });

    $('#intensitySlider').slider().on('slide click', function(e){
        eos.api('all', [e.value]);
    });

    $('#lightsToggle').change(function(item){
        eos.api(
            $(this).prop('checked') ? 'allon' : 'alloff',
            undefined,
            function(data){
                // update the view
                console.log(data);
            }
        );
    });

    function showFeedback(){

    }
});