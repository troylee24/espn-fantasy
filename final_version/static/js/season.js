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

function create_table(records, zscores, grades) {
    seasonTable = $(table_id).DataTable({
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
    window.onresize = function() {
        seasonTable.columns.adjust().draw('page');
    }

    let search_id = table_id + "_filter input"
    $(search_id)
        .off()
        .on('keyup', function() {
            seasonTable.column(2).search(this.value).draw();
        });
    
    return seasonTable;
}

function load_season() {
    let cats = [];
    let visible_cols = [];
    let hidden_cols = [];
    $.each($("#catsContainer .btn"), function() {
        let cat = $(this).text();
        let show = $(this).attr('aria-pressed') === "false";
        if (show) {
            cats.push(cat);
            visible_cols.push(col_index[cat]);
        }
        else {
            hidden_cols.push(col_index[cat]);
        }
    });

    let season_id = $("#seasonButton").text();
    $.ajax({
        url: '/load_season',
        type: 'POST',
        contentType: 'application/json',
        dataType: 'json',
        data: JSON.stringify({
            'season_id': season_id,
            'cats': cats
        })
    })
    .done(function(data) {
        let records = data['records']
        let grades = data['grades']
        let zscores = data['zscores']
        
        if ($.fn.dataTable.isDataTable(table_id)) {
            $(table_id).DataTable().clear().destroy();
        }
        seasonTable = create_table(records, zscores, grades);
        seasonTable
            .columns(hidden_cols).visible(false, false)
            .columns(visible_cols).visible(true, false)
            .column(1).search($("#fantasyTeamButton").attr("value"))
            .draw();
    });
}

// BEFORE DOCUMENT READY
$("#seasonButton").text(default_season);
$("#fantasyTeamButton").text("-- Show All Teams --");
$("#fantasyTeamButton").attr("value", "");
var table_id = "#seasonTable"

// WHEN DOCUMENT READY
$(document).ready(function () {
    // initial season table
    load_season(default_season);

    // change season table
    $("#seasonDropdown .dropdown-menu .dropdown-item").on('click', function (e) {
        let season_id = $(this).text();
        $("#seasonButton").text(season_id);
        load_season();
    });

    // filter by fantasy team
    $("#fantasyTeamDropdown .dropdown-menu .dropdown-item").on('click', function (e) {
        let fantasy_team = $(this).attr("value");
        $("#fantasyTeamButton").attr("value", fantasy_team);
        $("#fantasyTeamButton").text($(this).text());
        $(table_id).DataTable().column(1).search(fantasy_team).draw();
    });

    $(".btn").on('mousedown', function(e) {
        e.preventDefault();
        $(this).blur();
    });

    $("#showCategoriesButton").on('click', function() {
        load_season();
    });

});