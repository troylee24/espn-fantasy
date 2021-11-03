$(document).ready(function() {
    // DATATABLE INITIIALIZATION
    $("#recordTable").DataTable({
        "ajax": {
            "url": records_json,
            "dataSrc": ""
        },
        "columns": record_columns,
        "scrollX": true,
        "pageLength": 10,
        "lengthMenu": [
            [10, 25, 50, -1],
            [10, 25, 50, "All"]
        ],
        "columnDefs": [
            {
                "targets": [1],
                "searchable": true,
            },
            {
                "targets": "_all",
                "searchable": false,
            },
            {
                "targets": [1, 2, 3, 4, 5, 6, 8, 9, 10, 11],
                "orderSequence": ["desc", "asc"], 
            },
            {
                "targets": "_all",
                "createdCell": function (td, _cellData, _rowData, row, col) {
                    let key = record_headers[col]
                    let color = grades[row][key]
                    $(td).css('background-color', color)
                }
            }
        ],
    });
    $("#rankTable").DataTable({
        "ajax": {
            "url": ranks_json,
            "dataSrc": ""
        },
        "columns": rank_columns,
        "scrollX": true,
        "pageLength": 10,
        "lengthMenu": [
            [10, 25, 50, -1],
            [10, 25, 50, "All"]
        ],
        "columnDefs": [
            {
                "targets": [1],
                "searchable": true,
            },
            {
                "targets": "_all",
                "searchable": false,
            },
            {
                "targets": "_all",
                "createdCell": function (td, _cellData, _rowData, row, col) {
                    let key = rank_headers[col]
                    let color = grades[row][key]
                    $(td).css('background-color', color)
                }
            }
        ],
    });
});