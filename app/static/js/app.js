// Shared interface behaviour. Owner: Moksh.
(function () {
  "use strict";

  // Mobile navigation toggle
  var toggle = document.querySelector("[data-nav-toggle]");
  var nav = document.getElementById("site-nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", String(open));
    });
  }

  // Search button shows "Searching..." while the next page loads
  var searchForm = document.querySelector("[data-search-form]");
  if (searchForm) {
    searchForm.addEventListener("submit", function () {
      var button = searchForm.querySelector("button[type=submit]");
      if (button) {
        button.disabled = true;
        button.textContent = button.getAttribute("data-loading-text") || "Loading...";
      }
    });
  }

  // Forms with data-confirm ask before submitting (used for Delete)
  document.querySelectorAll("form[data-confirm]").forEach(function (form) {
    form.addEventListener("submit", function (event) {
      if (!window.confirm(form.getAttribute("data-confirm"))) {
        event.preventDefault();
      }
    });
  });
})();
