$(document).ready(function() {
    let reloaded = JSON.parse(sessionStorage.getItem("reloaded")) || false;
    let checkbox_states = JSON.parse(sessionStorage.getItem("checkbox_states")) || {};
    if (reloaded){
        $.each(checkbox_states, function(key, value) {
            $("#" + key).prop('checked', value);
        });
    }
    else {
        $.each(checkbox_states, function(key, value) {
            $("#" + key).prop('checked', true);
        });
    }
    sessionStorage.setItem("reloaded", false);

    $("#reloadDataButton").on('click', function(e) {
        $("#loader").show()
        e.preventDefault();
        let checked_cats = []

        $.each($(".cat-input"), function(){
            let checked = $(this).is(":checked");
            let col_i = $(this).attr('col_i');
            let cat_i = $(this).attr('cat_i');

            checkbox_states[$(this).attr('id')] = checked;
            if (checked) { checked_cats.push(cat_i); }
            
            $(table_id).DataTable().column(col_i)
                .visible(checked);
        });
        sessionStorage.setItem("checkbox_states", JSON.stringify(checkbox_states));

        let js_data = JSON.stringify(checked_cats);
        $.ajax({
            url: '/reload_data',
            type: 'post',
            contentType: 'application/json',
            dataType: 'json',
            data: js_data
        }).done(function() {
            sessionStorage.setItem("reloaded", JSON.stringify(true))
            window.location.reload()
        });
    });

});