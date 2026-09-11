/**
 * Expense X-Ray — Chart Initialization
 * Updated for Luxury Brown, Beige & Cream Theme.
 * Preserves original initDashboardCharts() signature.
 */

window.initDashboardCharts = function (categoryData, totalExpense) {
  const ctx = document.getElementById('categoryChart');
  if (!ctx) return;

  const labels = Object.keys(categoryData);
  const values = Object.values(categoryData);

  // Palette requested by user:
  // #6B4F3A (Espresso), #B86F52 (Terracotta Rust), #C49A5A (Ochre Gold), #7A8B68 (Sage Green)
  const palette = [
    '#6B4F3A',
    '#B86F52',
    '#C49A5A',
    '#7A8B68',
    '#D4A373',
    '#C5B4A5'
  ];

  if (window.myDashboardChart) {
    window.myDashboardChart.destroy();
  }

  if (labels.length === 0) {
    window.myDashboardChart = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: ['No Expenses'],
        datasets: [{
          data: [1],
          backgroundColor: ['#26201B'],
          borderColor: '#1C1714',
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '76%',
        plugins: {
          legend: { display: false },
          tooltip: { enabled: false }
        }
      }
    });
    return;
  }

  window.myDashboardChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [{
        data: values,
        backgroundColor: palette.slice(0, labels.length),
        borderColor: '#1C1714',
        borderWidth: 2,
        hoverOffset: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '74%',
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          backgroundColor: '#1C1714',
          titleColor: '#F7EFE9',
          bodyColor: '#C8B9AB',
          borderColor: '#D4A373',
          borderWidth: 1,
          padding: 10,
          displayColors: true,
          callbacks: {
            label: function (context) {
              const val = context.raw || 0;
              const pct = totalExpense > 0 ? ((val / totalExpense) * 100).toFixed(1) : 0;
              return `  ₹${val.toLocaleString('en-IN')} (${pct}%)`;
            }
          }
        }
      }
    }
  });
};
