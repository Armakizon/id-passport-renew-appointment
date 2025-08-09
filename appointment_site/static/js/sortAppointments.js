document.addEventListener("DOMContentLoaded", () => {
  const table = document.getElementById("appointmentsTable");
  const headers = table.querySelectorAll("th.sortable");
  let currentSortColumn = -1;
  let currentSortAsc = true;

  headers.forEach((th, index) => {
    // Save original label for reset
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
          const dateA = new Date(valA);
          const dateB = new Date(valB);
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
      tbody.innerHTML = "";
      sortedRows.forEach(row => tbody.appendChild(row));
    });
  });
});
