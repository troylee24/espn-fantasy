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
    let table = $(table_id).DataTable({
        "stateSave": true,
        "stateDuration": -1,
        "visible": false,
        "data": records,
        "columns": columns,
        "language": { "search": "Search Players:" },
        "scrollX": true,
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
                "targets": [2],
                "width": "189px"
            },
            {
                "targets": [0, 1],
                "width": "auto"
            },
            {
                "targets": "_all",
                "width": "32px"
            },
            {
                "targets": "_all",
                "createdCell": function (td, cellData, rowData, row, col) {
                    let key = headers[col]
                    let color = grades[row][key]
                    $(td).css('background-color', color)
                }
            }
        ]
    });

    let search_bar_name = table_id + "_filter input";
    $(search_bar_name)
        .off()
        .on('keyup', function() {
            table.column(2).search(this.value).draw();
        });
});