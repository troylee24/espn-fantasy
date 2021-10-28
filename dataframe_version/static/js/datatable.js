var records, columns, cols, grades;

function initVars(records, columns, cols, grades) {
    records = records;
    columns = columns;
    cols = cols;
    grades = grades
}

$(document).ready(function() {
    var statsTable = $("#statsTable").DataTable({
        "data": records,
        "columns": columns,
        "language": { "search": "Search Players:" },
        "scrollX": true,
        "pageLength": 25,
        "lengthMenu": [
            [10, 25, 50, 100, -1],
            [10, 25, 50, 100, "All"]
        ],
        "order": [[5, "asc"]],
        "columnDefs": [
            {
                "targets": [0, 1, 2, 3],
                "visible": false,
            },
            {
                "targets": [4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
                "searchable": false,
            },
            {
                "orderSequence": ["desc", "asc"], "targets": [8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]
            },
            {
                "width": "31px", "targets": [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]
            },
            {
                "width": "186px", "targets": [5]
            },
            {
                "targets": "_all",
                "createdCell": function (td, cellData, rowData, row, col) {
                    var key = cols[col]
                    var color = grades[row][key]
                    $(td).css('background-color', color)
                }
            }
        ],
        initComplete: function () {
            var hiddenColumns = {
                0: "Fantasy Team",
                1: "Season Year",
                2: "Season View",
                3: "Stats View",
            }
            this.api().columns(Object.keys(hiddenColumns)).every( function () {
                var column = this;
                var div = $('<div></div>')
                var span = $('<span>'+hiddenColumns[column.index()]+'</span>')
                span.appendTo(div)
                var select = $('<select class="selectpicker"><option value=""></option></select>')
                    .appendTo( $(div) )
                    .on( 'change', function () {
                        var val = $.fn.dataTable.util.escapeRegex(
                            $(this).val()
                        );

                        column
                            .search( val ? '^'+val+'$' : '', true, false )
                            .draw();
                    } );
                div.appendTo('#filterContainer')
                column.data().unique().sort().each( function ( d, j ) {
                    select.append( '<option value="'+d+'">'+d+'</option>' )
                } );
            } );
        }
    })

    $('.form-check-input').change(function(e) {
        e.preventDefault();
        var column = statsTable.column( $(this).attr('column') );
        column.visible( ! column.visible() );
    } );

    $('#statsTable_filter input')
        .off()
        .on('keyup', function() {
            statsTable.column(5).search(this.value).draw();
        });
});