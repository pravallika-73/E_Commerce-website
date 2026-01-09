let salesTimeChart;
let salesCategoryChart;

async function fetchKpis(start, end) {
  const params = new URLSearchParams();
  if (start) params.append('start', start);
  if (end) params.append('end', end);

  const res = await fetch('/api/kpis?' + params.toString());
  return res.json();
}

function updateKpiCards(data) {
  document.getElementById('kpiTotalSales').innerText = data.total_sales.toFixed(2);
  document.getElementById('kpiNumOrders').innerText = data.num_orders;
  document.getElementById('kpiAOV').innerText = data.aov.toFixed(2);
}

function renderSalesOverTime(data) {
  const ctx = document.getElementById('salesOverTimeChart').getContext('2d');
  const labels = data.sales_by_date.map(item => item.date);
  const values = data.sales_by_date.map(item => item.total_sales);

  if (salesTimeChart) salesTimeChart.destroy();

  salesTimeChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        label: 'Sales over time',
        data: values,
        borderColor: 'blue',
        fill: false
      }]
    }
  });
}

function renderSalesByCategory(data) {
  const ctx = document.getElementById('salesByCategoryChart').getContext('2d');
  const labels = data.sales_by_category.map(item => item.category);
  const values = data.sales_by_category.map(item => item.total_sales);

  if (salesCategoryChart) salesCategoryChart.destroy();

  salesCategoryChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Sales by category',
        data: values,
        backgroundColor: 'orange'
      }]
    }
  });
}

async function loadDashboard() {
  const start = document.getElementById('startDate').value;
  const end = document.getElementById('endDate').value;
  const data = await fetchKpis(start, end);
  updateKpiCards(data);
  renderSalesOverTime(data);
  renderSalesByCategory(data);
}

// Remove PDF listener completely (keep this commented)
///*
// document.getElementById('downloadPdfBtn').addEventListener('click', () => {
//   const start = document.getElementById('startDate').value;
//   const end = document.getElementById('endDate').value;
//   const params = new URLSearchParams();
//   if (start) params.append('start', start);
//   if (end) params.append('end', end);
//   window.location = '/api/report/pdf?' + params.toString();
// });
//*/

// initial load (whole dataset)
loadDashboard();
// initial load (whole dataset)
loadDashboard();

// Download CSV for current filters
document.getElementById('downloadCsvBtn').addEventListener('click', () => {
  const start = document.getElementById('startDate').value;
  const end = document.getElementById('endDate').value;
  const params = new URLSearchParams();
  if (start) params.append('start', start);
  if (end) params.append('end', end);
  window.location = '/api/report/csv?' + params.toString();
});
