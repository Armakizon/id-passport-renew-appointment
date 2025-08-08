// notifyForm.js

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

    // Get branch names from buttons
    const locationButtons = document.getElementById("locationButtons");
    const branchNames = [];
    if (locationButtons) {
      locationButtons.querySelectorAll("button.location-btn").forEach(btn => {
        branchNames.push(btn.textContent.trim());
      });
    }

    // Build branch list string with max 3 shown + "and x other branches"
    const maxBranchesToShow = 3;
    let displayedBranches = "";
    if (branchNames.length === 0) {
      displayedBranches = "no branches selected";
    } else if (branchNames.length <= maxBranchesToShow) {
      displayedBranches = branchNames.join(", ");
    } else {
      const firstThree = branchNames.slice(0, maxBranchesToShow).join(", ");
      const othersCount = branchNames.length - maxBranchesToShow;
      displayedBranches = `${firstThree} and ${othersCount} other branch${othersCount > 1 ? "es" : ""}`;
    }

    // Set confirmation message HTML with line breaks
    messageEl.innerHTML = `
      You are about to sign up to get notified for these branches:<br><strong>${displayedBranches}</strong><br><br>
      From: <strong>${document.getElementById("startDate")?.value || "any date"}</strong><br>
      To: <strong>${document.getElementById("endDate")?.value || "any date"}</strong>.<br><br>
      Proceed?
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
