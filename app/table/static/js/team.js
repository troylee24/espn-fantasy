function create_table(table_id, data, zscores, grades, columns, headers) {
    let sort_order = table_id == "#recordTable" ? ["desc", "asc"] : ["asc", "desc"]
    let table = $(table_id).DataTable({
        "data": data,
        "columns": columns,
        "scrollX": true,
        "autoWidth": false,
        "lengthChange": false,
        "paging": false,
        "info": false,
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
                "targets": [11],
                "orderSequence": ["desc", "asc"]
            },
            {
                "targets": [2, 3, 4, 5, 6, 8, 9, 10],
                "orderSequence": sort_order, 
            },
            {
                "targets": [0],
                "width": "22px"
            },
            {
                "targets": [1],
                "width": "160px"
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
    let search_id = table_id + "_filter input"
    $(search_id)
        .off()
        .on('keyup', function() {
            table.column(1).search(this.value).draw();
        });

    window.onresize = function() {
        $.fn.dataTable.tables({api: true}).columns.adjust().draw('page');
    }
}

function load_team() {
    $.ajax({
        url: load_team_url,
        type: 'POST',
        dataType: 'json'
    })
    .done(function(data) {
        let records = data['records']
        let zscores = data['zscores']
        let grades = data['grades']
        let ranks = data['ranks']

        create_table("#recordTable", records, zscores, grades, record_columns, record_headers)
        create_table("#rankTable", ranks, zscores, grades, rank_columns, rank_headers)
    });
}

$(document).ready(function() {
    load_team()
});