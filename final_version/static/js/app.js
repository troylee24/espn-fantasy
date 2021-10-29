$(document).ready(function() {
    let checkbox_states = JSON.parse(sessionStorage.getItem("checkbox_states")) || {};
    $.each(checkbox_states, function(key, value) {
        $("#" + key).prop('checked', value);
    });

    $("#reloadDataButton").on('click', function(e) {
        $("#loader").show()
        e.preventDefault();
        let visible_table = $.fn.dataTable.tables({visible: true, api: true});
        let checked_cats = []

        $.each($(".cat-input"), function(){
            let checked = $(this).is(":checked");
            let col_i = $(this).attr('col_i');
            let cat_i = $(this).attr('cat_i');

            checkbox_states[$(this).attr('id')] = checked;
            if (checked) { checked_cats.push(cat_i); }
            
            let column = visible_table.column(col_i);
            column.visible(checked);
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
            location.reload()
        });
    });

});