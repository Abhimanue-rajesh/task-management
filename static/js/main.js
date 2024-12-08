//Spinner
const spinnerWrapperEl = document.querySelector(".spinner-wrapper");
window.addEventListener("load", () => {
  spinnerWrapperEl.style.opacity = "0";
  setTimeout(() => {
    spinnerWrapperEl.style.display = "none";
  }, 200);
});

function goBackAndRefresh() {
  window.location.href = document.referrer;
  window.addEventListener("pageshow", function (event) {
    if (event.persisted) {
      window.location.reload();
    }
  });
}

document.addEventListener("DOMContentLoaded", function () {
  // Add click event to all rows with the 'clickable-row' class
  document.querySelectorAll(".clickable-row").forEach(function (row) {
    row.addEventListener("click", function () {
      const href = this.dataset.href;
      if (href) {
        window.location.href = href;
      }
    });
  });
});
