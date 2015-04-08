/**
 * Created by rulkens on 03/04/15.
 */
$(document).ready(function(){

    var eos = new Eos();

    $('#stepSlider').slider().on('click slide', function(e){
        eos.api('only', [e.value, 1]);
    });

    $('#intensitySlider').slider().on('click slide', function(e){
        eos.api('all', [e.value]);
    });

    // for all the individual lights
    $('[data-light-num]').slider();
    $('[data-light-num]').on('click slide', function(e){
        var id = $(this).data('light-num');
        eos.api('one', [id, e.value]);
    });

    $('#lightsToggle').change(function(item){
        eos.api(
            $(this).prop('checked') ? 'allon' : 'alloff',
            undefined,
            function(data){
                // update the view

            }
        );
    });

    function showFeedback(){

    }
});