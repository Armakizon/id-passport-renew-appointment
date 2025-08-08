// distanceFilter.js

function haversineDistance(lat1, lon1, lat2, lon2) {
  const toRad = angle => (angle * Math.PI) / 180;
  const R = 6371; // Earth radius in km
  const dLat = toRad(lat2 - lat1);
  const dLon = toRad(lon2 - lon1);
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(toRad(lat1)) *
    Math.cos(toRad(lat2)) *
    Math.sin(dLon / 2) ** 2;
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}

document.addEventListener("DOMContentLoaded", () => {
  const applyBtn = document.getElementById("applyDistanceFilter");
  const distanceInput = document.getElementById("distanceInput");
  const distanceWarning = document.getElementById("distanceWarning");
  const locationButtons = document.getElementById("locationButtons");

  if (!applyBtn || !distanceInput || !distanceWarning || !locationButtons) {
    console.error("Some elements for distance filter not found");
    return;
  }

  applyBtn.addEventListener("click", () => {
    const maxDistance = parseFloat(distanceInput.value);

    if (!window.userHasSelectedLocation) {
      distanceWarning.style.display = "block";
      distanceWarning.classList.add("shake");
      setTimeout(() => distanceWarning.classList.remove("shake"), 500);
      return;
    } else {
      distanceWarning.style.display = "none";
    }

    if (isNaN(maxDistance) || maxDistance <= 0) {
      alert("Please enter a valid positive number for max distance.");
      return;
    }

    locationButtons.innerHTML = "";
    window.activeBranchIds = [];

    for (const [id, info] of Object.entries(branch_map)) {
      const branchLat = info.lat;
      const branchLon = info.lon;

      if (branchLat == null || branchLon == null) {
        console.warn(`Branch ${id} missing coordinates`);
        continue;
      }

      const dist = haversineDistance(window.userLat, window.userLon, branchLat, branchLon);

      if (dist <= maxDistance) {
        window.activeBranchIds.push(id);

        const btn = document.createElement("button");
        btn.className = "btn btn-secondary btn-sm location-btn";
        btn.textContent = `${info.name} - ${info.address}`;
        btn.onclick = () => {
          window.activeBranchIds = window.activeBranchIds.filter(bid => bid !== id);
          locationButtons.removeChild(btn);
          if (typeof updateTableVisibility === "function") {
            updateTableVisibility();
          }
        };

        locationButtons.appendChild(btn);
      }
    }

    if (typeof updateTableVisibility === "function") {
      updateTableVisibility();
    }
  });
});
