// scripts.js - dashboard interactivity and Chart initialization
// Extracted from user_dashboard template to central static file.

document.addEventListener("DOMContentLoaded", function () {
  const navItems = document.querySelectorAll(".nav-item, .nav-btn");
  const views = document.querySelectorAll(".view");
  const charts = {}; // store Chart instances to avoid re-creating

  // --- Dynamic Greeting ---
  const greetingEl = document.getElementById("dynamic-greeting");
  if (greetingEl) {
    const hour = new Date().getHours();
    let greeting = "Welcome back";
    if (hour < 12) greeting = "Good morning";
    else if (hour < 18) greeting = "Good afternoon";
    else greeting = "Good evening";
    
    const currentText = greetingEl.innerText;
    const username = currentText.replace("Welcome back, ", "");
    greetingEl.innerText = `${greeting}, ${username}`;
  }

  function showView(name) {
    views.forEach((v) => v.classList.remove("active"));
    const el = document.getElementById("view-" + name);
    if (el) {
      el.classList.add("active");
      localStorage.setItem('active_view', name);
    }
  }

  // Get active view from localStorage or default to dashboard
  const activeView = localStorage.getItem('active_view') || 'dashboard';
  showView(activeView);
  navItems.forEach((item) => {
    if (item.dataset.view === activeView) {
      item.classList.add("active");
    } else {
      item.classList.remove("active");
    }
  });
  // initialize default active view chart
  initChartForView(activeView);

  // attach click handlers
  navItems.forEach((item) => {
    item.addEventListener("click", function () {
      navItems.forEach((i) => i.classList.remove("active"));
      this.classList.add("active");
      const view = this.dataset.view;
      showView(view);
      // initialize chart for that view lazily
      initChartForView(view);
    });
  });

  // Example chart initializers. Replace sample data with real context/JSON as needed.
  function initChartForView(view) {
    if (charts[view]) return; // already created
    
    // Parse the embedded JSON data
    let chartData = null;
    const dataEl = document.getElementById("chart-data");
    if (dataEl) {
      try {
        chartData = JSON.parse(dataEl.textContent);
      } catch(e) { console.error("Could not parse chart data", e); }
    }

    const cfg = {
      dashboard: () => {
        if (!chartData) return;
        // monthly expenses - line
        const el = document.getElementById("chart-monthly-expenses");
        if (el) {
          const ctx = el.getContext("2d");
          const gradient = ctx.createLinearGradient(0, 0, 0, 400);
          gradient.addColorStop(0, "rgba(11,99,212,0.4)");
          gradient.addColorStop(1, "rgba(11,99,212,0.0)");

          charts.dashboard_monthly = new Chart(ctx, {
            type: "line",
            data: {
              labels: [
                "Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
              ],
              datasets: [
                {
                  label: "Expenses",
                  data: chartData.monthly_data,
                  borderColor: "#0b63d4",
                  backgroundColor: gradient,
                  fill: true,
                  tension: 0.4,
                  borderWidth: 3,
                  pointBackgroundColor: "#fff",
                  pointBorderColor: "#0b63d4",
                  pointRadius: 4,
                  pointHoverRadius: 6
                },
              ],
            },
            options: { 
              responsive: true,
              plugins: { legend: { display: false } },
              scales: {
                x: { grid: { display: false } },
                y: { border: { dash: [4, 4] }, grid: { color: "rgba(0,0,0,0.05)" } }
              },
              animation: {
                y: { duration: 2000, easing: 'easeOutBounce' }
              }
            },
          });
        }

        const el2 = document.getElementById("chart-by-category");
        if (el2) {
          const ctx2 = el2.getContext("2d");
          charts.dashboard_cat = new Chart(ctx2, {
            type: "doughnut",
            data: {
              labels: chartData.cat_labels,
              datasets: [
                {
                  data: chartData.cat_values,
                  backgroundColor: [
                    "#4e79a7", "#f28e2b", "#e15759", "#76b7b2", "#59a14f",
                  ],
                  borderWidth: 0,
                  hoverOffset: 6
                },
              ],
            },
            options: { 
              responsive: true,
              cutout: '75%',
              plugins: { legend: { position: 'bottom' } },
              animation: { animateScale: true, animateRotate: true }
            },
          });
        }
      },

      transactions: () => {
        const el = document.getElementById("chart-transactions");
        if (!el) return;
        const ctx = el.getContext("2d");
        charts.transactions = new Chart(ctx, {
          type: "bar",
          data: {
            labels: Array.from({ length: 30 }, (_, i) => i + 1),
            datasets: [
              {
                label: "Transactions",
                data: Array.from({ length: 30 }, () => Math.floor(Math.random() * 6)),
                backgroundColor: "#0b63d4",
              },
            ],
          },
          options: { responsive: true },
        });
      },

      budget: () => {
        if (!chartData) return;
        const el = document.getElementById("chart-budget");
        if (!el) return;
        const ctx = el.getContext("2d");
        charts.budget = new Chart(ctx, {
          type: "bar",
          data: {
            labels: chartData.budget_labels,
            datasets: [
              {
                label: "Budgeted",
                data: chartData.budget_allocated,
                backgroundColor: "#76b7b2",
              },
              {
                label: "Spent",
                data: chartData.budget_spent,
                backgroundColor: "#e15759",
              },
            ],
          },
          options: { responsive: true },
        });
      },

      reports: () => {
        const el = document.getElementById("chart-yearly");
        if (!el) return;
        const ctx = el.getContext("2d");
        charts.reports = new Chart(ctx, {
          type: "line",
          data: {
            labels: ["2019", "2020", "2021", "2022", "2023", "2024"],
            datasets: [
              {
                label: "Total Spent",
                data: [6000, 7200, 6800, 7500, 7900, 8200],
                borderColor: "#4e79a7",
                fill: false,
              },
            ],
          },
          options: { responsive: true },
        });
      },

      saving_goals: () => {
        const el = document.getElementById("chart-savings");
        if (!el) return;
        const ctx = el.getContext("2d");
        charts.savings = new Chart(ctx, {
          type: "pie",
          data: {
            labels: ["Emergency", "Vacation", "Car"],
            datasets: [
              {
                data: [60, 25, 15],
                backgroundColor: ["#59a14f", "#f28e2b", "#e15759"],
              },
            ],
          },
          options: { responsive: true },
        });
      },

      reports: () => {
        if (!chartData) return;
        
        // Top 5 Categories Horizontal Bar
        const el = document.getElementById("chart-top-categories");
        if (el && chartData.top5_labels && chartData.top5_labels.length > 0) {
          const ctx = el.getContext("2d");
          charts.reports_top = new Chart(ctx, {
            type: "bar",
            data: {
              labels: chartData.top5_labels,
              datasets: [{
                label: "Зарцуулалт",
                data: chartData.top5_values,
                backgroundColor: [
                  "#4e79a7", "#f28e2b", "#e15759", "#76b7b2", "#59a14f"
                ],
                borderWidth: 0,
                borderRadius: 6,
              }],
            },
            options: {
              indexAxis: "y",
              responsive: true,
              plugins: { legend: { display: false } },
              scales: {
                x: { grid: { color: "rgba(0,0,0,0.05)" } },
                y: { grid: { display: false } }
              },
              animation: { duration: 1200, easing: 'easeOutQuart' }
            },
          });
        }
        
        // Yearly Trend Line (reuse monthly_data)
        const el2 = document.getElementById("chart-yearly-trend");
        if (el2 && chartData.monthly_data) {
          const ctx2 = el2.getContext("2d");
          const gradient = ctx2.createLinearGradient(0, 0, 0, 300);
          gradient.addColorStop(0, "rgba(78, 121, 167, 0.3)");
          gradient.addColorStop(1, "rgba(78, 121, 167, 0.0)");
          
          charts.reports_trend = new Chart(ctx2, {
            type: "line",
            data: {
              labels: [
                "1-р сар", "2-р сар", "3-р сар", "4-р сар", "5-р сар", "6-р сар",
                "7-р сар", "8-р сар", "9-р сар", "10-р сар", "11-р сар", "12-р сар",
              ],
              datasets: [{
                label: "Зарцуулалт",
                data: chartData.monthly_data,
                borderColor: "#4e79a7",
                backgroundColor: gradient,
                fill: true,
                tension: 0.4,
                borderWidth: 2.5,
                pointBackgroundColor: "#fff",
                pointBorderColor: "#4e79a7",
                pointRadius: 4,
                pointHoverRadius: 7,
              }],
            },
            options: {
              responsive: true,
              plugins: { legend: { display: false } },
              scales: {
                x: { grid: { display: false } },
                y: { border: { dash: [4, 4] }, grid: { color: "rgba(0,0,0,0.05)" } }
              },
              animation: { duration: 1500, easing: 'easeOutQuart' }
            },
          });
        }
      },
    };

    // call the initializer if exists
    const fn = cfg[view];
    if (fn) fn();
  }

  // initialize default (dashboard)
  initChartForView("dashboard");
});

// --- Lightbox Functions for Receipts ---
window.openLightbox = function(imgUrl, caption) {
  const lightbox = document.getElementById("receipt-lightbox");
  const lightboxImg = document.getElementById("lightbox-img");
  const lightboxCaption = document.getElementById("lightbox-caption");
  
  if (lightbox && lightboxImg) {
    lightboxImg.src = imgUrl;
    if (lightboxCaption) {
      lightboxCaption.textContent = caption || "Баримтын зураг";
    }
    lightbox.classList.add("active");
  }
};

window.closeLightbox = function() {
  const lightbox = document.getElementById("receipt-lightbox");
  if (lightbox) {
    lightbox.classList.remove("active");
  }
};

window.selectCommonExpense = function(inputEl) {
  const val = inputEl.value;
  const datalist = document.getElementById("common-expenses-list");
  if (!datalist) return;
  
  let matchedOption = null;
  for (let i = 0; i < datalist.options.length; i++) {
    if (datalist.options[i].value === val) {
      matchedOption = datalist.options[i];
      break;
    }
  }
  
  if (matchedOption) {
    const categoryId = matchedOption.getAttribute("data-category-id");
    
    // Autofill description
    const descField = document.getElementById("id_exp-description");
    if (descField) {
      descField.value = val;
    }
    
    // Autofill category
    const catField = document.getElementById("id_exp-category");
    if (catField && categoryId) {
      catField.value = categoryId;
    }
    
    // Focus on amount field
    const amtField = document.getElementById("id_exp-amount");
    if (amtField) {
      amtField.focus();
    }
    
    // Clear search box
    inputEl.value = "";
  }
};


