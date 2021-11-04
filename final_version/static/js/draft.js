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
    $('button[data-bs-toggle="tab"]').on( 'shown.bs.tab', function () {
        $.fn.dataTable.tables( {visible: true, api: true} ).columns.adjust();
    } );

    // DATATABLE INITIIALIZATION
    let playersTable = $("#playersTable").DataTable({
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

    $("#playersTable_filter input")
        .off()
        .on('keyup', function() {
            playersTable.column(2).search(this.value).draw();
        });

    let teamTable = $("#teamTable").DataTable({
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
            // {
            //     "targets": "_all",
            //     "type": "empty-on-bottom"
            // },
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
        ],
    });

    $("#teamTable_filter input")
        .off()
        .on('keyup', function() {
            teamTable.column(2).search(this.value).draw();
        });
    
    window.onresize = function() {
        $(".table").DataTable().columns.adjust().draw('page');
    }
    
    $("#playersTable tbody").on('click', 'tr', function() {
        let tr = this;
        playersTable.columns(1).visible(true);
        let new_row = playersTable.row(tr).node().cloneNode(true);
        teamTable.row.add(new_row).draw();
        playersTable.columns(1).visible(false);
        $(tr).css("background-color", "#E5E5E5");
        setTimeout(function () {
            $(tr).css("background-color", "");
        }, 50);
    });

    $("#teamTable tbody").on('click', 'tr', function() {
        let tr = this
        $(tr).css("background-color", "#E5E5E5");
        setTimeout(function () {
            teamTable.row(tr).remove().draw();
        }, 20);
    });
});