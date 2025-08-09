// static/js/main.js

const allRows = [...document.querySelectorAll("#appointmentsTable tbody tr")];
const searchInput = document.getElementById("branchSearch");
const resultsList = document.getElementById("branchResults");
const getLocationButton = document.getElementById("getLocationButton");

window.activeBranchIds = [];
window.userHasSelectedLocation = false;

const branchNames = [...new Set(allRows.map(row => {
  const id = row.getAttribute("data-branch-id");
  const name = row.children[0].textContent.trim();
  return `${id}|${name}`;
}))];

function applyAlternatingRowColors() {
  const rows = Array.from(document.querySelectorAll("#appointmentsTable tbody tr"))
    .filter(row => row.style.display !== "none");

  rows.forEach((row, index) => {
    if (index % 2 === 0) {
      row.style.backgroundColor = "#fff"; // even row color
    } else {
      row.style.backgroundColor = "#f9fbff"; // odd row color (lighter tint)
    }
  });
}

function updateTableVisibility(showEarliestOnly = false) {
  const grouped = {};
  allRows.forEach(row => {
    const id = row.getAttribute("data-branch-id");
    (grouped[id] ||= []).push(row);
  });

  const urlParams = new URLSearchParams(window.location.search);
  const startDate = urlParams.get("start_date");
  const endDate = urlParams.get("end_date");

  allRows.forEach(row => row.style.display = "none");

  for (const [branchId, rows] of Object.entries(grouped)) {
    if (window.activeBranchIds.length === 0 || window.activeBranchIds.includes(branchId)) {
      const filteredRows = rows.filter(row => {
        const dateStr = row.children[2]?.innerText?.trim();  // Adjust index if needed
        if (!dateStr) return false;

        const rowDate = new Date(dateStr);
        const start = startDate ? new Date(startDate) : null;
        const end = endDate ? new Date(endDate) : null;

        if (start && rowDate < start) return false;
        if (end && rowDate > end) return false;

        return true;
      });

      if (showEarliestOnly) {
        filteredRows.sort((a, b) =>
          new Date(a.children[2].innerText) - new Date(b.children[2].innerText)
        )[0]?.style && (filteredRows[0].style.display = "");
      } else {
        filteredRows.forEach(row => row.style.display = "");
      }
    }
  }

  // Call the alternating row colors function after visibility updates
  applyAlternatingRowColors();
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

        const rowDate = new Date(dateStr);

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

// Initialize display on page load
updateTableVisibility();
