// dateFilter.js
document.addEventListener("DOMContentLoaded", () => {
  const startDate = document.getElementById("startDate");
  const endDate = document.getElementById("endDate");

  if (!startDate || !endDate) return; // Safety check

  const params = new URLSearchParams(window.location.search);
  if (params.has("start_date")) startDate.value = params.get("start_date");
  if (params.has("end_date")) endDate.value = params.get("end_date");

  function updateDateParams() {
    const url = new URL(window.location);
    if (startDate.value) {
      url.searchParams.set("start_date", startDate.value);
    } else {
      url.searchParams.delete("start_date");
    }

    if (endDate.value) {
      url.searchParams.set("end_date", endDate.value);
    } else {
      url.searchParams.delete("end_date");
    }

    // Update URL without reloading the page
    history.pushState(null, "", url);
    
    // Call the function to update table visibility if it exists
    if (typeof updateTableVisibility === "function") {
      updateTableVisibility();
    }
  }

  startDate.addEventListener("change", updateDateParams);
  endDate.addEventListener("change", updateDateParams);
});
