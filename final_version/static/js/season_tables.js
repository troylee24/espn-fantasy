var __emptyOnBottom = function(a, b, low) {
    a = a || low;
    b = b || low;
    return ((a < b) ? -1 : ((a > b) ? 1 : 0));   
}
jQuery.extend( jQuery.fn.dataTableExt.oSort, {
    "empty-on-bottom-asc": function (a, b) {
        return __emptyOnBottom(a, b, Number.POSITIVE_INFINITY)
    },
    "empty-on-bottom-desc": function (a, b) {
    return __emptyOnBottom(a, b, Number.NEGATIVE_INFINITY) * -1
    },
});

$(document).ready(function() {
    // DATATABLE INITIIALIZATION
    let table = $(table_id).DataTable({
        "ajax": {
            "url": records_json,
            "dataSrc": ""
        },
        "columns": columns,
        "scrollX": true,
        "autoWidth": false,
        "language": { "search": "Search Players:" },
        "pageLength": 10,
        "lengthMenu": [
            [10, 25, 50, -1],
            [10, 25, 50, "All"]
        ],
        "columnDefs": [
            {
                "targets": "_all",
                "type": "empty-on-bottom"
            },
            {
                "targets": [1],
                "visible": false
            },
            {
                "targets": [1, 2],
                "searchable": true
            },
            {
                "targets": "_all",
                "searchable": false,
            },
            {
                "targets": [5, 6, 7, 8, 9, 10, 11, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22],
                "orderSequence": ["desc", "asc"], 
            },
            {
                "targets": 2,
                "width": "155px"
            },
            {
                "targets": [0, 3, 5],
                "width": "22px"
            },
            {
                "targets": "_all",
                "width": "30px"
            },
            {
                "targets": "_all",
                "createdCell": function (td, _cellData, _rowData, row, col) {
                    let key = headers[col]
                    let color = grades[row][key]
                    $(td).css('background-color', color)
                }
            }
        ],
    });

    window.onresize = function() {
        table.columns.adjust().draw('page');
    }

    let search_bar_name = table_id + "_filter input";
    $(search_bar_name)
        .off()
        .on('keyup', function() {
            table.column(2).search(this.value).draw();
        });

    // FILTERING CATEGORIES
    $("#showCategoriesButton").on('click', function() {
        $(this).prop("disabled", true);
        let checked_cats = []

        $.each($(".cat-input"), function(){
            let checked = $(this).is(":checked");
            let col_i = $(this).attr('col_i');
            let cat_i = $(this).attr('cat_i');

            if (checked) {
                checked_cats.push(cat_i);
            }
            table.column(col_i).visible(checked, false);
        });
        table.columns.adjust().draw('page');

        data = {};
        data["season_id"] = season_id;
        data["checked_cats"] = checked_cats;
        dataJSON = JSON.stringify(data);

        $.ajax({
            url: '/show_categories',
            type: 'POST',
            contentType: 'application/json',
            dataType: 'json',
            data: dataJSON
        }).done(function() {
            $.ajax({
                url: grades_json,
                dataType: "json",
            }).done(function(data) {
                grades = data;
                table.ajax.reload( function() {
                    $("#showCategoriesButton").prop("disabled", false);
                });
            });
        });
    });
});