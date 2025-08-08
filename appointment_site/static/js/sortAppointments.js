// sortAppointments.js
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("#appointmentsTable th.sortable").forEach(th => {
    th.dataset.label = th.textContent.trim();

    th.addEventListener("click", () => {
      const column = th.cellIndex;
      const table = document.getElementById("appointmentsTable");
      const rows = Array.from(table.querySelector("tbody").rows);
      const isAscending = th.dataset.sorted !== "asc";

      // Clear previous sort indicators and states
      document.querySelectorAll("#appointmentsTable th.sortable").forEach(header => {
        header.innerHTML = header.dataset.label;
        delete header.dataset.sorted;
      });

      th.dataset.sorted = isAscending ? "asc" : "desc";
      th.innerHTML = `${th.dataset.label} <span class="sort-indicator">${isAscending ? "↑" : "↓"}</span>`;

      const sorted = rows.sort((a, b) => {
        let valA = a.cells[column].textContent.trim();
        let valB = b.cells[column].textContent.trim();

        const numA = parseFloat(valA.replace(",", ""));
        const numB = parseFloat(valB.replace(",", ""));
        const isDateColumn = column === 2;

        if (isDateColumn) {
          const dateA = new Date(valA);
          const dateB = new Date(valB);
          if (!isNaN(dateA) && !isNaN(dateB)) {
            return isAscending ? dateA - dateB : dateB - dateA;
          }
        }

        if (!isNaN(numA) && !isNaN(numB)) {
          return isAscending ? numA - numB : numB - numA;
        }

        return isAscending
          ? valA.localeCompare(valB, undefined, { numeric: true })
          : valB.localeCompare(valA, undefined, { numeric: true });
      });

      const tbody = table.querySelector("tbody");
      tbody.innerHTML = "";
      sorted.forEach(row => tbody.appendChild(row));
    });
  });
});
