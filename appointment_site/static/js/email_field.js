document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("notifyForm");
  const modal = document.getElementById("confirmationModal");
  const messageEl = document.getElementById("confirmationMessage");
  const confirmBtn = document.getElementById("confirmBtn");
  const cancelBtn = document.getElementById("cancelBtn");

  form.addEventListener("submit", function (event) {
    event.preventDefault();

    // Fill hidden inputs
    document.getElementById("locationsInput").value = JSON.stringify(window.activeBranchIds || []);
    document.getElementById("fromDateInput").value = document.getElementById("startDate")?.value || "";
    document.getElementById("toDateInput").value = document.getElementById("endDate")?.value || "";

    // Get branch names from buttons (only name part, no address)
    const locationButtons = document.getElementById("locationButtons");
    const branchNames = [];
    if (locationButtons) {
      locationButtons.querySelectorAll("button.location-btn").forEach(btn => {
        const fullText = btn.textContent.trim();
        const branchName = fullText.split(" - ")[0]; // extract name before " - "
        branchNames.push(branchName);
      });
    }

    // Build branch list string with max 3 shown + "and x other branches", each on a new line
    const maxBranchesToShow = 3;
    let displayedBranches = "";
    if (branchNames.length === 0) {
      displayedBranches = "לא נבחרו לשכות";
    } else if (branchNames.length <= maxBranchesToShow) {
      displayedBranches = branchNames.join("<br>");
    } else {
      const firstThree = branchNames.slice(0, maxBranchesToShow).join("<br>");
      const othersCount = branchNames.length - maxBranchesToShow;
      displayedBranches = `${firstThree}<br>and ${othersCount} other branch${othersCount > 1 ? "es" : ""}`;
    }

    // Set confirmation message HTML with line breaks
    messageEl.innerHTML = `
       אתם עומדים להירשם לרשימת התפוצה עבור הלשכות הבאות<br><strong>${displayedBranches}</strong><br><br>
      מתאריך: <strong>${document.getElementById("startDate")?.value || "כל תאריך"}</strong><br>
      עד תאריך: <strong>${document.getElementById("endDate")?.value || "כל תאריך"}</strong>.<br><br>
      המשך?
    `;

    modal.style.display = "flex";
  });

  confirmBtn.addEventListener("click", () => {
    modal.style.display = "none";
    form.submit();
  });

  cancelBtn.addEventListener("click", () => {
    modal.style.display = "none";
  });
});
