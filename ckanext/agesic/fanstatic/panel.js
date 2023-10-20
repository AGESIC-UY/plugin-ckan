google.charts.load('current', {'packages':['bar', 'corechart', 'table']});
google.charts.setOnLoadCallback(drawDatasetTable);
google.charts.setOnLoadCallback(drawDatasetBarChart);
google.charts.setOnLoadCallback(drawShowcaseTable);
google.charts.setOnLoadCallback(drawShowcasesBarChart);
google.charts.setOnLoadCallback(drawResourcesTable);
google.charts.setOnLoadCallback(drawResourcesBarChart);
google.charts.setOnLoadCallback(drawResourcesPieChart);
google.charts.setOnLoadCallback(drawResoucesLicensePieChart);
google.charts.setOnLoadCallback(drawResoucesFormatPieChart);
google.charts.setOnLoadCallback(drawOrganizationsTable);
google.charts.setOnLoadCallback(drawCreate_table_total);

function drawGenericTable(path, columnName, elementID) {
  $.ajax({
    url: path,
    dataType: "json",
    type: "GET",
    contentType: "application/json; charset=utf-8",
    success: function (data) {
      let tvalues = new google.visualization.DataTable();
      tvalues.addColumn('string', columnName);
      tvalues.addColumn('number', 'Total');
      $.each(data, function (index, value) {
          tvalues.addRow([value.Type, value.Count]);
      });
      var formatter = new google.visualization.NumberFormat({
        fractionDigits: '0',
        groupingSymbol: '.',
        negativeParens: true,
      });
      formatter.format(tvalues, 1);
      tvalues.setColumnProperty(1, 'className', 'customCell');
      let table = new google.visualization.Table(document.getElementById(elementID));
      table.draw(tvalues, {showRowNumber: false, width: '100%', height: '100%'});
    }
  });
}

function drawGenericBarChart(path, dataArr, elementID, options = {}, mobileOptions = {}) {
  $.ajax({
    url: path,
    dataType: "json",
    type: "GET",
    contentType: "application/json; charset=utf-8",
    success: function (data) {
      let size = dataArr.getNumberOfColumns()
      $.each(data, function (index, value) {
        if (size === 3)
          dataArr.addRow([value.Year.toString(), value.Created, value.Updated]);
        else
          dataArr.addRow([value.Year.toString(), value.Created]);
      });
        var formatter = new google.visualization.NumberFormat({
            groupingSymbol: '.',
            fractionDigits: '0',
            language: 'es-UY'
        });
        formatter.format(dataArr, 1);
                var view = new google.visualization.DataView(dataArr);
        view.setColumns([0, 1,
                       { calc: "stringify",
                         sourceColumn: 1,
                         type: "string",
                         role: "annotation" },
                       ]);
        var chart = new google.visualization.ColumnChart(document.getElementById(elementID));
        if (window.innerWidth <= 480) {
            chart.draw(view, google.charts.Bar.convertOptions(mobileOptions));
        } else {
            chart.draw(view, google.charts.Bar.convertOptions(options));
        }
        window.addEventListener('resize', function() {
        if (window.innerWidth <= 480) {
        chart.draw(view, google.charts.Bar.convertOptions(mobileOptions));
            } else {
        chart.draw(view, google.charts.Bar.convertOptions(options));
          }
        })
      }
  });
}

function drawDatasetTable() {
  drawGenericTable("/agesic/charts/table_datasets_total", 'Conjuntos', 'chart_dataset_table_div');
}

function drawDatasetBarChart() {
  var datasets = new google.visualization.DataTable();
  datasets.addColumn('string', 'Año');
  datasets.addColumn('number', 'Conjuntos publicados');
  var options = {
    legend: { position: 'none' },
    fontSize: 16,
    vAxis: {
      title: 'Conjuntos publicados',
      textStyle: {
        color: '#757575',
      },
      titleTextStyle: {
        italic: false,
      },
    },
    hAxis: {
      title: 'años',
      textStyle: {
        color: '#757575'
      },
      titleTextStyle: {
        italic: false,
      },
    },
    colors: ['#0099FF', '#1AA3FF', '#33ADFF'],
    annotations: {
      alwaysOutside: true,
      textStyle: {
        fontSize: 16,
        bold: true,
        color: '#000',
      },
    }
  };
  var mobileOptions = {
    legend: { position: 'none' },
    fontSize: 10,
    responsive: true,
    vAxis: {
      title: 'Conjuntos publicados',
      textStyle: {
        color: '#757575',
      },
      titleTextStyle: {
        italic: false,
      },
    },
    hAxis: {
      title: 'años',
      textStyle: {
        color: '#757575',
      },
      titleTextStyle: {
        italic: false,
      },
    },
    colors: ['#0099FF', '#1AA3FF', '#33ADFF'],
    annotations: {
      textStyle: {
        fontSize: 10,
        color: '#000',
      },
    },
  };
  drawGenericBarChart("/agesic/charts/chart_datasets_enabled", datasets, 'chart_dataset_div', options, mobileOptions);
}

function drawResourcesTable() {
  drawGenericTable("/agesic/charts/table_resources_total", 'Recursos', 'chart_resources_table_div');
}

function drawResourcesBarChart() {
  var resources = new google.visualization.DataTable();
  resources.addColumn('string', 'Año');
  resources.addColumn('number', 'Recursos publicados');
  var options = {
    legend: { position: 'none' },
    fontSize: 16,
    vAxis: {
      title: 'Recursos publicados',
      textStyle: {
        color: '#757575'
      },
      titleTextStyle: {
        italic: false,
      },
    },
    hAxis: {
      title: 'años',
      textStyle: {
        color: '#757575',
      },
      titleTextStyle: {
        italic: false,
      },
    },
    colors: ['#D23948', '#7E5495', '#916CA4'],
    annotations: {
      alwaysOutside: true,
      textStyle: {
        fontSize: 16,
        bold: true,
        color: '#000',
      },
    },
  };
  var mobileOptions = {
    legend: { position: 'none' },
    fontSize: 10,
    responsive: true,
    vAxis: {
    title: 'Recursos publicados',
    textStyle: {
        color: '#757575',
      },
      titleTextStyle: {
        italic: false,
      },
    },
    hAxis: {
      title: 'años',
      textStyle: {
        color: '#757575',
      },
      titleTextStyle: {
        italic: false,
      },
    },
    colors: ['#D23948', '#6C3B86', '#7E5495'],
    annotations: {
      textStyle: {
        fontSize: 10,
        color: '#000',
      },
    },
  };
  drawGenericBarChart("/agesic/charts/chart_resources_enabled", resources, 'chart_resources_div', options, mobileOptions);
}

function drawShowcaseTable() {
  drawGenericTable("/agesic/charts/table_showcases_total", 'Aplicaciones', 'chart_showcase_table_div');
}

function drawShowcasesBarChart() {
  var showcases = new google.visualization.DataTable();
  showcases.addColumn('string', 'Año');
  showcases.addColumn('number', 'Aplicaciones publicadas');
  var options = {
    legend: { position: 'none' },
    fontSize: 16,
    vAxis: {
      title: 'Aplicaciones publicadas',
      textStyle: {
        color: '#757575'
      },
      titleTextStyle: {
        italic: false,
      },
    },
    hAxis: {
      title: 'años',
      textStyle: {
        color: '#757575'
      },
      titleTextStyle: {
        italic: false,
      },
    },
    colors: ['#28A745', '#3EB058', '#53B96A'],
    annotations: {
      alwaysOutside: true,
      textStyle: {
        fontSize: 16,
        bold: true,
        color: '#000',
      },
    },
  };
  var mobileOptions = {
    legend: { position: 'none' },
    fontSize: 10,
    responsive: true,
    vAxis: {
      title: 'Aplicaciones publicadas',
      textStyle: {
        color: '#757575',
      },
      titleTextStyle: {
        italic: false,
      },
    },
    hAxis: {
      title: 'años',
      textStyle: {
        color: '#757575',
      },
      titleTextStyle: {
        italic: false,
      },
    },
    colors: ['#28A745', '#3EB058', '#53B96A'],
    annotations: {
      textStyle: {
        fontSize: 12,
        color: '#000', // Color de los valores flotantes
      },
    },
  };
  drawGenericBarChart("/agesic/charts/chart_showcases_enabled", showcases, 'chart_showcase_div', options, mobileOptions);
}

function drawResourcesPieChart() {
  $.ajax({
    url: "/agesic/charts/table_resources_total",
    dataType: "json",
    type: "GET",
    contentType: "application/json; charset=utf-8",
    success: function (data) {
      var resources = [['Recursos', 'Total']];
      $.each(data, function (index, value) {
        if (index > 0)
          resources.push([value.Type, value.Count]);
      });
      var figures = google.visualization.arrayToDataTable(resources);
      var formatter = new google.visualization.NumberFormat({
            groupingSymbol: '.',
            fractionDigits: '0',
        });
      formatter.format(figures, 1);
      var options = {
      pieSliceTextStyle: {
      color: 'black',
      fontSize: 13,
      },
      legend: 'derecha',
      maxLines: 10,
      chartArea: {
        width: '80%',
        height: '80%'
      },
        responsive: true,
        maintainAspectRatio: false,
        colors: ['#FF0000', '#FF6900', '#DAAA00', '#28A745', '#470A68', '#CF99FA', '#003DA5', '#0099FF', '#FA1251', '#FF69B4', '#FFE800', '#CD2334', '#950C2E', '#F7B290', '#F3A303'],
        tooltip: {
          trigger: 'selection',
        },
      };
      var chart = new google.visualization.PieChart(document.getElementById('chart_resources_by_url_div'));
      chart.draw(figures, options);
       google.visualization.events.addListener(figures, 'select', function() {
    // Obtiene la sección seleccionada
    var selection = chart.getSelection();
    // Si hay una sección seleccionada
    if (selection.length > 0) {
      // Obtiene los datos de la sección seleccionada
      var dataItem = figures.getValue(selection[0].row, 0);
      var dataValue = figures.getValue(selection[0].row, 1);
      var tooltip = document.createElement('div');
      tooltip.setAttribute('class', 'tooltip');
      tooltip.innerHTML = dataItem + ': ' + dataValue;
      document.body.appendChild(tooltip);
    }
  });
  document.addEventListener('click', function(event) {
    if (event.target.tagName !== 'DIV' || event.target.getAttribute('class') !== 'tooltip') {
      var tooltips = document.getElementsByClassName('tooltip');
      for (var i = 0; i < tooltips.length; i++) {
        document.body.removeChild(tooltips[i]);
        }
      }
    });
   }
 });
};

function drawResoucesFormatPieChart() {
  $.ajax({
    url: "/agesic/charts/resources_by_format",
    dataType: "json",
    type: "GET",
    contentType: "application/json; charset=utf-8",
    success: function (data) {
      var resources = [
          ['Extensiones', 'Total']
        ];
      $.each(data, function (index, value) {
        resources.push([value.Type, value.Count]);
      });
      var figures = google.visualization.arrayToDataTable(resources);
        var formatter = new google.visualization.NumberFormat({
            groupingSymbol: '.',
            fractionDigits: '0',
        });
      formatter.format(figures, 1);
      var options = {

      pieSliceTextStyle: {
      color: 'black',
      fontSize: 13,
      },
      legend: {
      scrollwheel: true,
      maxLines: null,
      },
      chartArea: {
        width: '100%',
        height: '100%',
      },
        responsive: true,
        maintainAspectRatio: false,
        colors: ['#FF0000', '#FF6900', '#DAAA00', '#28A745', '#003DA5', '#470A68', '#FA1251', '#F3A303', '#8DE746', '#0099FF','#CF99FA', '#FFE800', '#CD2334', '#950C2E', '#FF69B4', '#F7B290'],
        tooltip: {
          trigger: 'selection',
        }
      };
      var chart = new google.visualization.PieChart(document.getElementById('chart_resources_by_format_div'));
      chart.draw(figures, options);
       google.visualization.events.addListener(figures, 'select', function() {
    // Obtiene la sección seleccionada
    var selection = chart.getSelection();
    // Si hay una sección seleccionada
    if (selection.length > 0) {
      // Obtiene los datos de la sección seleccionada
      var dataItem = figures.getValue(selection[0].row, 0);
      var dataValue = figures.getValue(selection[0].row, 1);
      var tooltip = document.createElement('div');
      tooltip.setAttribute('class', 'tooltip');
      tooltip.innerHTML = dataItem + ': ' + dataValue;
      document.body.appendChild(tooltip);
    }
  });
  document.addEventListener('click', function(event) {
    if (event.target.tagName !== 'DIV' || event.target.getAttribute('class') !== 'tooltip') {
      var tooltips = document.getElementsByClassName('tooltip');
      for (var i = 0; i < tooltips.length; i++) {
        document.body.removeChild(tooltips[i]);
        }
      }
    });
   }
 });
};

function drawResoucesLicensePieChart() {
  $.ajax({
    url: "/agesic/charts/resources_by_license",
    dataType: "json",
    type: "GET",
    contentType: "application/json; charset=utf-8",
    success: function (data) {
      var resources = [
          ['Licencias', 'Total']
        ];
      $.each(data, function (index, value) {
        resources.push([value.Type, value.Count]);
      });
      var figures = google.visualization.arrayToDataTable(resources);
      var formatter = new google.visualization.NumberFormat({
            groupingSymbol: '.',
            fractionDigits: '0',
        });
      formatter.format(figures, 1);
      var options = {
      pieSliceTextStyle: {
      color: 'black',
      fontSize: 13,
      },
      legend: {position: 'derecha',
      maxLines: 10,
      alignment: 'start'},
      chartArea: {
        width: '80%',
        height: '80%'
      },
        responsive: true,
        colors: ['#FF0000', '#FF6900', '#DAAA00', '#28A745', '#470A68', '#CF99FA', '#003DA5', '#0099FF', '#FA1251', '#FF69B4', '#FFE800', '#CD2334', '#950C2E', '#F7B290', '#F3A303'],
        tooltip: {
          trigger: 'selection',
        }
      };
      var chart = new google.visualization.PieChart(document.getElementById('chart_resources_by_license_div'));
      chart.draw(figures, options);
      google.visualization.events.addListener(figures, 'select', function() {
    // Obtiene la sección seleccionada
    var selection = chart.getSelection();
    // Si hay una sección seleccionada
    if (selection.length > 0) {
      // Obtiene los datos de la sección seleccionada
      var dataItem = figures.getValue(selection[0].row, 0);
      var dataValue = figures.getValue(selection[0].row, 1);
      var tooltip = document.createElement('div');
      tooltip.setAttribute('class', 'tooltip');
      tooltip.innerHTML = dataItem + ': ' + dataValue;
      document.body.appendChild(tooltip);
    }
  });
  document.addEventListener('click', function(event) {
    if (event.target.tagName !== 'DIV' || event.target.getAttribute('class') !== 'tooltip') {
      var tooltips = document.getElementsByClassName('tooltip');
      for (var i = 0; i < tooltips.length; i++) {
        document.body.removeChild(tooltips[i]);
        }
      }
    });
   }
 });
}

function drawOrganizationsTable() {
  $.ajax({
    url: "/agesic/charts/table_organizations_total",
    dataType: "json",
    type: "GET",
    contentType: "application/json; charset=utf-8",
    success: function (data) {
      var values = new google.visualization.DataTable();
      values.addColumn('string', 'Publicadores');
      values.addColumn('number', 'Cantidad de conjuntos');
      values.addColumn('number', 'Cantidad de recursos');
      $.each(data, function (index, value) {
        values.addRow([value.Organization, value.Datasets, value.Resources]);
      });
      var view = new google.visualization.DataView(values);
      values.sort({column: 1, desc: true})
      values.setColumnProperty(0, 'className', 'customCellOrgCol0');
      values.setColumnProperty(1, 'className', 'customCellOrg');
      values.setColumnProperty(2, 'className', 'customCellOrg');
      view.setRows([0,1,2,3,4,5,6,7,8,9]);
      view.setRows(view.getSortedRows({column: 0, sortOrder: 'desc'}));
      var formatter = new google.visualization.NumberFormat({
        fractionDigits: '0',
        groupingSymbol: '.',
        negativeParens: true,
      });
      formatter.format(values, 1);
      formatter.format(values, 2);
      var table = new google.visualization.Table(document.getElementById('chart_organization_table_div'));
      table.draw(view, {showRowNumber: false, width: '100%', height: '100%'});
    }
  });
}
function drawCreate_table_total(){
$.ajax({
    url: "/agesic/charts/table_organizations_total",
    dataType: "json",
    type: "GET",
    contentType: "application/json; charset=utf-8",
    success: function (data) {
      var values = new google.visualization.DataTable();
      values.addColumn('number', 'Total de Publicadores');
      values.addRow([data.length])
      values.setColumnProperty(0, 'className', 'customCellOrg');
      var table = new google.visualization.Table(document.getElementById('chart_organization_table_total'));
      table.draw(values, {showRowNumber: false, width: '100%', height: '100%'});
    }
  });
}
