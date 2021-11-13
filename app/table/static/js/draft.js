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

function create_players_table(records, zscores, grades, teamTable) {
    let table_id = "#playersTable"
    let playersTable = $(table_id).DataTable({
        "data": records,
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

    $(table_id + "_filter input")
        .off()
        .on('keyup', function() {
            playersTable.column(2).search(this.value).draw();
        });
    
    $(table_id + " tbody").on('click', 'tr', function() {
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
}

function create_team_table() {
    table_id = "#teamTable"
    let teamTable = $(table_id).DataTable({
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
        ],
    });

    $(table_id + "_filter input")
        .off()
        .on('keyup', function() {
            teamTable.column(2).search(this.value).draw();
        });

    $(table_id + " tbody").on('click', 'tr', function() {
        let tr = this
        $(tr).css("background-color", "#E5E5E5");
        setTimeout(function () {
            teamTable.row(tr).remove().draw();
        }, 20);
    });

    return teamTable
}

function load_draft() {
    $.ajax({
        url: load_draft_url,
        type: 'POST',
        contentType: 'application/json',
        dataType: 'json',
        data: JSON.stringify({
            'season_id': season_id,
        })
    })
    .done(function(data) {
        let records = data['records']
        let zscores = data['zscores']
        let grades = data['grades']
        
        teamTable = create_team_table();
        create_players_table(records, zscores, grades, teamTable);
        window.onresize = function() {
            $.fn.dataTable.tables( {api: true} ).columns.adjust();
        }
    });
}

$(document).ready(function() {
    $('button[data-bs-toggle="tab"]').on( 'shown.bs.tab', function () {
        $.fn.dataTable.tables( {visible: true, api: true} ).columns.adjust();
    } );
    
    load_draft();
});