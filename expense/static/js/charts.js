// Initialize charts if elements exist

window.initDashboardCharts = function(categoryData, totalExpense) {
    const ctx = document.getElementById('categoryPieChart');
    if (!ctx) return;
    
    Chart.defaults.color = '#7d6b5d';
    Chart.defaults.font.family = 'Inter';

    const labels = Object.keys(categoryData);
    const data = Object.values(categoryData);
    
    // Nice vibrant warm colors for brown/beige theme
    const colors = [
        '#a67b5b', '#c49a76', '#e0c097', '#8b5f42', '#d2b48c', '#6b4c3a'
    ];

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors,
                borderWidth: 0,
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: { color: '#f8fafc' }
                }
            },
            cutout: '70%'
        }
    });
};
