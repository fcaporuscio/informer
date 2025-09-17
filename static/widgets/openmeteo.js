/* Open-Meteo Widget JS */

window.addEventListener('load', (event) => {

  class OpenMeteo extends informer.Widget {
    start() {
      this.chart = null;
      this.current_temperature = this.node.querySelector(".current-temperature");
      this.relative_humidity = this.node.querySelector(".relhum");
      this.setRefreshInterval(2 * 60);
    }

    receiveData(data) {
      const units = data.units;

      // Current
      const current = data?.current || {};
      this.current_temperature.innerText = current.temperature.toFixed(1) + units;
      this.relative_humidity.innerText = current.relative_humidity.toFixed(0) + "%";

      if(this.params.graph) {
        const chart_id = "chart-" + (this.params?.wid || "unknown");
        const ctx = document.getElementById(chart_id);

        if(this.chart != null) {
          this.chart.destroy();
        }
        else {
          informer.removeClass(ctx, "loader");
        }

        const config = this._make_chart_config(data, units);
        this.chart = new Chart(ctx, config);
      }
    }

    _make_chart_config(data, units) {
      var i, il, d;

      const hourly_data = data?.hourly || {};
      const daily_data = data?.daily || {};
      const day_names = data?.day_names || null;

      var temperature = [],
          precip_mm = [],
          daily_max = [],
          daily_min = [],
          daily_minmax = [],
          num_days = 1;

      var label_precipitation = "Precipitation";
      var precipitation_units = "mm";

      // Hourly
      for(i = 0, il = hourly_data.temperature.length; i < il; i++) {
        var d = hourly_data.temperature[i];
        temperature.push({ x: d[0], y: d[1] });
      }

      for(i = 0, il = hourly_data.precipitation.length; i < il; i++) {
        var d = hourly_data.precipitation[i];
        precip_mm.push({ x: d[0], y: d[1] });
      }

      // Daily
      for(i = 0, il = daily_data.temperature_max.length; i < il; i++) {
        var d = daily_data.temperature_max[i];
        daily_max.push({ x: d[0], y: d[1] });
      }

      for(i = 0, il = daily_data.temperature_min.length; i < il; i++) {
        var d = daily_data.temperature_min[i];
        var idx = daily_min.length;
        daily_min.push({ x: d[0], y: d[1] });
        daily_minmax.push({ x: d[0], y: [d[1], daily_max[idx].y] });
      }

      num_days = daily_max.length - 1;

      // Prepare Datasets
      const dataset_temperature = {
        type: "line",
        stepped: false,
        label: 'Temperature',
        data: temperature,
        xAxisID: 'x-hourly-temp',
        borderColor: informer.theme.accent_color,
        backgroundColor: informer.theme.accent_color,
        borderWidth: 1,
        order: 1,
        tension: 0.2,
        pointRadius: function(context) {
          const dt = new Date(context.raw.x).getTime();
          const now = Date.now();
          const dist = Math.abs((now - dt) / 1000);
          return (now > dt && dist <= 3600) ? 4 : 0;
        }
      };

      const dataset_precipitation = {
        type: "line",
        stepped: true,
        fill: true,
        label: label_precipitation,
        data: precip_mm,
        xAxisID: 'x-hourly-precip',
        yAxisID: 'y-precip',
        borderColor: informer.theme.section_active_color,
        backgroundColor: informer.theme.section_active_color,
        borderWidth: 1,
        pointRadius: 0,
        tension: 0.2,
        order: 2,
      };

      const dataset_daily_max = {
        type: "line",
        stepped: true,
        fill: false,
        label: 'Max',
        data: daily_max,
        xAxisID: 'x-hourly-temp',
        borderColor: informer.theme.failure_color,
        backgroundColor: informer.theme.failure_color,
        borderWidth: 1,
        pointRadius: 0,
        order: 4,
        tension: 0.8
      };

      const dataset_daily_min = {
        type: "line",
        stepped: true,
        fill: false,
        label: 'Min',
        data: daily_min,
        xAxisID: 'x-hourly-temp',
        borderColor: informer.theme.success_color,
        backgroundColor: informer.theme.success_color,
        borderWidth: 1,
        pointRadius: 0,
        order: 3,
        tension: 0.8
      };

      const chart_scales = {
        'x-hourly-precip': {
          beginAtZero: true,
          type: 'time',
          position: 'top',
          time: {
            unit: 'day',
            displayFormats: { day: 'MMM d' },
            tooltipFormat: "MMM d, h:mm a",
          },
          title: { display: false, text: 'Daily' },
          grid: { color: informer.theme.widget_border_color },
          ticks: {
            callback: function(value, index, values) {
              const prefix = day_names != null && day_names.length > index ? day_names[index] + " " : "";
              const date = luxon.DateTime.fromMillis(value);
              const day = parseInt(date.toFormat('d'));

              if(index === 0 || day === 1) {
                return prefix + date.toFormat("MMM d")
              }
              return prefix + date.toFormat("d");
            }
          }
        },

        'x-hourly-temp': {
          type: 'time',
          position: 'bottom',
          time: {
            unit: 'hour',
            displayFormats: { hour: 'h a' },
            tooltipFormat: "MMM d, h:mm a",
          },
          title: { display: false, text: 'Hourly' },
          grid: { color: informer.theme.widget_border_color },
          ticks: {
            callback: function(value, index, ticks) {
               const date = luxon.DateTime.fromMillis(value);
               return date.toFormat('ha').toLowerCase();
            }
          }
        },

        y: {
          title: {
            type: "linear",
            position: "left",
            display: false,
            text: 'Temperature'
          },
          grid: { color: informer.theme.widget_border_color },
          ticks: {
            callback: function(value, index, ticks) {
              return value + units;
            }
          }
        },

        'y-precip': {
          type: "linear",
          position: "right",
          title: { display: true, text: "Precipitation (" + precipitation_units + ")" },
          min: 0,
          grid: { drawOnChartArea: false },
          ticks: {
            callback: function(value, index, ticks) {
              const suffix = ""; //precipitation_units;
              var v = value;
              if(v < 1) {
                v = "< 1";
              }
              else {
                v = v.toString();
              }
              return v + suffix;
            }
          }
        }
      };

      const do_animation = this.params.animation === true && this.chart == null;

      const chart_options = {
        animation: do_animation,
        interaction: { mode: 'index', intersect: false },
        elements: {
          line: {
            stepped: 'after'
          }
        },
        maintainAspectRatio: false,
        responsive: true,
        plugins: {
          title: {
            display: true,
            text: num_days == 1 ? "Today's Forcast" : `${num_days}-day Forecast`
          },
          legend: {
            display: true,
            position: 'bottom',
            labels: { boxWidth: 10 }
          },
          tooltip: {
            callbacks: {
              label: function(context) {
                let label = context.dataset.label || '';
                const isPrecip = (label == label_precipitation);
                if (label) {
                  label += ': ';
                }
                return label + context.formattedValue + (isPrecip ? "mm" : units); 
              }
            }
          }
        },
        scales: chart_scales
      };

      var datasets = [];
      datasets.push(dataset_temperature);
      datasets.push(dataset_precipitation);

      if(!!this.params?.max) {
        datasets.push(dataset_daily_max)
      }

      if(!!this.params?.min) {
        datasets.push(dataset_daily_min)
      }

      // Build the config!
      var config = {
        type: 'line',
        data: {
          datasets: datasets
        },
        options: chart_options
      };

      return config;
    }
  }

  informer.createWidgetsForClass(OpenMeteo);

});
