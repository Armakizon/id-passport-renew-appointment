// Helper to parse DD/MM/YYYY to Date object
function parseDateDMY(dateStr) {
  const [day, month, year] = dateStr.split("/").map(Number);
  return new Date(year, month - 1, day);
}

document.addEventListener("DOMContentLoaded", () => {
  const table = document.getElementById("appointmentsTable");
  const headers = table.querySelectorAll("th.sortable");
  let currentSortColumn = -1;
  let currentSortAsc = true;

  headers.forEach((th, index) => {
    // Add sort indicator span if missing
    if (!th.querySelector(".sort-indicator")) {
      const arrowSpan = document.createElement("span");
      arrowSpan.className = "sort-indicator";
      arrowSpan.textContent = "";
      th.appendChild(arrowSpan);
    }

    th.addEventListener("click", () => {
      const column = index;

      if (currentSortColumn === column) {
        currentSortAsc = !currentSortAsc;
      } else {
        currentSortAsc = true;
      }
      currentSortColumn = column;

      // Reset indicators
      headers.forEach((header) => {
        header.dataset.sorted = "";
        header.querySelector(".sort-indicator").textContent = "";
      });

      th.dataset.sorted = currentSortAsc ? "asc" : "desc";
      th.querySelector(".sort-indicator").textContent = currentSortAsc ? "↑" : "↓";

      const rows = Array.from(table.tBodies[0].rows);

      const sortedRows = rows.sort((a, b) => {
        let valA = a.cells[column].textContent.trim();
        let valB = b.cells[column].textContent.trim();

        if (column === 3) {
          valA = valA === "-" ? Number.POSITIVE_INFINITY : parseFloat(valA.replace(",", ""));
          valB = valB === "-" ? Number.POSITIVE_INFINITY : parseFloat(valB.replace(",", ""));
          if (isNaN(valA)) valA = Number.POSITIVE_INFINITY;
          if (isNaN(valB)) valB = Number.POSITIVE_INFINITY;
          return currentSortAsc ? valA - valB : valB - valA;
        }

        if (column === 2) {
          const dateA = parseDateDMY(valA);
          const dateB = parseDateDMY(valB);
          if (!isNaN(dateA) && !isNaN(dateB)) {
            return currentSortAsc ? dateA - dateB : dateB - dateA;
          }
        }

        const numA = parseFloat(valA.replace(",", ""));
        const numB = parseFloat(valB.replace(",", ""));
        if (!isNaN(numA) && !isNaN(numB)) {
          return currentSortAsc ? numA - numB : numB - numA;
        }

        return currentSortAsc
          ? valA.localeCompare(valB, undefined, { numeric: true, sensitivity: "base" })
          : valB.localeCompare(valA, undefined, { numeric: true, sensitivity: "base" });
      });

      const tbody = table.tBodies[0];
      
      // Clear the tbody by removing rows, not by setting innerHTML
      while (tbody.firstChild) {
        tbody.removeChild(tbody.firstChild);
      }
      
      // Re-add the sorted rows
      sortedRows.forEach(row => tbody.appendChild(row));
      
      // Update the global allRows reference to maintain consistency
      if (typeof window !== 'undefined' && window.allRows) {
        window.allRows = sortedRows;
      }
    });
  });
});
