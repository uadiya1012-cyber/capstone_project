// scripts.js - dashboard interactivity and Chart initialization
// Extracted from user_dashboard template to central static file.

document.addEventListener("DOMContentLoaded", function () {
  const navItems = document.querySelectorAll(".nav-item");
  const views = document.querySelectorAll(".view");
  const charts = {}; // store Chart instances to avoid re-creating

  function showView(name) {
    views.forEach((v) => v.classList.remove("active"));
    const el = document.getElementById("view-" + name);
    if (el) el.classList.add("active");
  }

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

    const cfg = {
      dashboard: () => {
        // monthly expenses - line
        const el = document.getElementById("chart-monthly-expenses");
        if (el) {
          const ctx = el.getContext("2d");
          charts.dashboard_monthly = new Chart(ctx, {
            type: "line",
            data: {
              labels: [
                "Jan",
                "Feb",
                "Mar",
                "Apr",
                "May",
                "Jun",
                "Jul",
                "Aug",
                "Sep",
                "Oct",
                "Nov",
                "Dec",
              ],
              datasets: [
                {
                  label: "Expenses",
                  data: [
                    500, 700, 650, 800, 750, 900, 700, 850, 950, 700, 600, 800,
                  ],
                  borderColor: "#0b63d4",
                  backgroundColor: "rgba(11,99,212,0.08)",
                },
              ],
            },
            options: { responsive: true },
          });
        }

        const el2 = document.getElementById("chart-by-category");
        if (el2) {
          const ctx2 = el2.getContext("2d");
          charts.dashboard_cat = new Chart(ctx2, {
            type: "doughnut",
            data: {
              labels: ["Food", "Rent", "Transport", "Utilities", "Other"],
              datasets: [
                {
                  data: [300, 900, 120, 80, 50],
                  backgroundColor: [
                    "#4e79a7",
                    "#f28e2b",
                    "#e15759",
                    "#76b7b2",
                    "#59a14f",
                  ],
                },
              ],
            },
            options: { responsive: true },
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
                data: Array.from({ length: 30 }, () =>
                  Math.floor(Math.random() * 6),
                ),
                backgroundColor: "#0b63d4",
              },
            ],
          },
          options: { responsive: true },
        });
      },

      budget: () => {
        const el = document.getElementById("chart-budget");
        if (!el) return;
        const ctx = el.getContext("2d");
        charts.budget = new Chart(ctx, {
          type: "bar",
          data: {
            labels: ["Groceries", "Rent", "Entertainment", "Savings"],
            datasets: [
              {
                label: "Budgeted",
                data: [400, 1200, 200, 600],
                backgroundColor: "#76b7b2",
              },
              {
                label: "Spent",
                data: [350, 1200, 190, 250],
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
    };

    // call the initializer if exists
    const fn = cfg[view];
    if (fn) fn();
  }

  // initialize default (dashboard)
  initChartForView("dashboard");
});
