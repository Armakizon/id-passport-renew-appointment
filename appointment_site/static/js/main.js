// static/js/main.js

// Declare variables at module level but don't query DOM yet
let allRows = [];
let searchInput = null;
let resultsList = null;
let getLocationButton = null;
let branchNames = [];
let currentShowEarliestOnly = true; // Track current state

window.activeBranchIds = [];
window.userHasSelectedLocation = false;
window.currentShowEarliestOnly = currentShowEarliestOnly; // Expose globally

// Helper to parse DD/MM/YYYY to Date object
function parseDateDMY(dateStr) {
  const [day, month, year] = dateStr.split("/").map(Number);
  return new Date(year, month - 1, day);
}

// Function to refresh the allRows array to ensure it's in sync with DOM
function refreshAllRows() {
  allRows = [...document.querySelectorAll("#appointmentsTable tbody tr")];
  return allRows;
}

function updateTableVisibility(showEarliestOnly = null) {
  // If no parameter is passed, use the current state
  if (showEarliestOnly === null) {
    showEarliestOnly = currentShowEarliestOnly;
  } else {
    // Update the current state
    currentShowEarliestOnly = showEarliestOnly;
  }

  // Refresh the allRows array to ensure it's in sync with DOM
  refreshAllRows();

  const grouped = {};
  allRows.forEach(row => {
    const id = row.getAttribute("data-branch-id");
    (grouped[id] ||= []).push(row);
  });

  const urlParams = new URLSearchParams(window.location.search);
  const startDate = urlParams.get("start_date");
  const endDate = urlParams.get("end_date");

  // First, hide all rows
  allRows.forEach(row => row.style.display = "none");

  for (const [branchId, rows] of Object.entries(grouped)) {
    if (window.activeBranchIds.length === 0 || window.activeBranchIds.includes(branchId)) {
      const filteredRows = rows.filter(row => {
        const dateStr = row.children[2]?.innerText?.trim();
        if (!dateStr) return false;

        const rowDate = parseDateDMY(dateStr);
        const start = startDate ? new Date(startDate) : null;
        const end = endDate ? new Date(endDate) : null;

        if (start && rowDate < start) return false;
        if (end && rowDate > end) return false;

        return true;
      });

      if (showEarliestOnly) {
        // Show only the earliest date for each branch
        if (filteredRows.length > 0) {
          const earliestRow = filteredRows
            .sort((a, b) => parseDateDMY(a.children[2].innerText) - parseDateDMY(b.children[2].innerText))[0];
          if (earliestRow) {
            earliestRow.style.display = "";
          }
        }
      } else {
        // Show all dates for each branch
        filteredRows.forEach(row => {
          row.style.display = "";
        });
      }
    }
  }
}

function getFilteredEntries(startDate, endDate, activeBranchIds) {
  const grouped = {};
  allRows.forEach(row => {
    const id = row.getAttribute("data-branch-id");
    (grouped[id] ||= []).push(row);
  });

  const start = startDate ? new Date(startDate) : null;
  const end = endDate ? new Date(endDate) : null;

  const results = [];

  for (const [branchId, rows] of Object.entries(grouped)) {
    if (activeBranchIds.length === 0 || activeBranchIds.includes(branchId)) {
      const filteredRows = rows.filter(row => {
        const dateStr = row.children[2]?.innerText?.trim(); // Adjust index if needed
        if (!dateStr) return false;

        const rowDate = parseDateDMY(dateStr);

        if (start && rowDate < start) return false;
        if (end && rowDate > end) return false;

        return true;
      });

      filteredRows.forEach(row => {
        results.push({
          branchId,
          date: row.children[2].innerText.trim()
        });
      });
    }
  }

  return results;
}

// Initialize everything when DOM is ready to prevent forced reflows
document.addEventListener('DOMContentLoaded', function() {
  // Now safely query DOM elements
  allRows = [...document.querySelectorAll("#appointmentsTable tbody tr")];
  searchInput = document.getElementById("branchSearch");
  resultsList = document.getElementById("branchResults");
  getLocationButton = document.getElementById("getLocationButton");

  // Initialize branch names after DOM is ready
  branchNames = [...new Set(allRows.map(row => {
    const id = row.getAttribute("data-branch-id");
    const name = row.children[0].textContent.trim();
    return `${id}|${name}`;
  }))];

  // Ensure global variables are properly set
  window.currentShowEarliestOnly = currentShowEarliestOnly;
  window.allRows = allRows;

  // Initialize display after DOM is ready
  updateTableVisibility();

  // Filter drawer event handling
  const filterDrawer = document.getElementById('filterDrawer');
  if (filterDrawer) {
    filterDrawer.addEventListener('show.bs.offcanvas', function() {
      document.body.classList.add('offcanvas-open');
    });

    filterDrawer.addEventListener('hide.bs.offcanvas', function() {
      document.body.classList.remove('offcanvas-open');
    });
  }
});

// Dark mode functionality is handled by CSS
