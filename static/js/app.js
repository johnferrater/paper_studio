/*
 * Paper Studio — progressive enhancement layer.
 * No dependencies: every behaviour degrades gracefully without JavaScript.
 */
(function () {
  "use strict";

  /* --- Sidebar navigation (mobile drawer) -------------------------------- */

  function initNavigation() {
    var shell = document.querySelector(".app-shell");
    if (!shell) return;

    var openers = document.querySelectorAll("[data-nav-open]");
    var closers = document.querySelectorAll("[data-nav-close]");
    var lastFocused = null;

    function setOpen(isOpen) {
      shell.classList.toggle("is-nav-open", isOpen);
      document.body.style.overflow = isOpen ? "hidden" : "";
      openers.forEach(function (button) {
        button.setAttribute("aria-expanded", String(isOpen));
      });
    }

    openers.forEach(function (button) {
      button.addEventListener("click", function () {
        lastFocused = button;
        setOpen(!shell.classList.contains("is-nav-open"));
      });
    });

    closers.forEach(function (button) {
      button.addEventListener("click", function () {
        setOpen(false);
        if (lastFocused) lastFocused.focus();
      });
    });

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && shell.classList.contains("is-nav-open")) {
        setOpen(false);
        if (lastFocused) lastFocused.focus();
      }
    });
  }

  /* --- Confirmation for destructive or irreversible actions --------------- */

  function initConfirmations() {
    document.addEventListener("click", function (event) {
      var trigger = event.target.closest("[data-confirm]");
      if (!trigger) return;

      var message = trigger.getAttribute("data-confirm");
      if (!message) return;

      if (!window.confirm(message)) {
        event.preventDefault();
        event.stopPropagation();
      }
    });
  }

  /* --- Submit button loading state --------------------------------------- */

  function initSubmitStates() {
    document.addEventListener("submit", function (event) {
      var form = event.target;
      if (!(form instanceof HTMLFormElement)) return;
      if (form.dataset.submitting === "on") return;

      var submitter = event.submitter;
      var button = submitter || form.querySelector('[type="submit"]');
      if (!button) return;

      var label = button.getAttribute("data-loading-label") || "Saving…";
      form.dataset.submitting = "on";
      button.setAttribute("aria-busy", "true");
      button.classList.add("is-loading");
      button.setAttribute("title", label);
      button.dataset.originalLabel = button.textContent;
    });
  }

  /* --- Dismissible flash messages ---------------------------------------- */

  function initDismissibleAlerts() {
    document.addEventListener("click", function (event) {
      var button = event.target.closest("[data-alert-dismiss]");
      if (!button) return;
      var alert = button.closest(".alert");
      if (alert) alert.remove();
    });
  }

  /* --- Password visibility toggle ----------------------------------------- */

  var EYE_ICON =
    '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" ' +
    'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">' +
    '<path d="M2.5 10S5 5.5 10 5.5 17.5 10 17.5 10 15 14.5 10 14.5 2.5 10 2.5 10z"/>' +
    '<circle cx="10" cy="10" r="2.5"/></svg>';

  var EYE_OFF_ICON =
    '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" ' +
    'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">' +
    '<path d="M8 5.8A6.7 6.7 0 0 1 10 5.5c5 0 7.5 4.5 7.5 4.5a13 13 0 0 1-2.4 2.9"/>' +
    '<path d="M4.3 7.1A13.4 13.4 0 0 0 2.5 10S5 14.5 10 14.5c1 0 1.9-.2 2.7-.5"/>' +
    '<path d="M8 8.2a2.7 2.7 0 0 0 3.8 3.8"/><path d="m3.5 3.5 13 13"/></svg>';

  function buildToggle(field) {
    var toggle = document.createElement("button");
    toggle.type = "button";
    toggle.className = "password-field__toggle";
    toggle.setAttribute("data-password-toggle", field.id);
    toggle.setAttribute("aria-label", "Show password");
    toggle.setAttribute("aria-pressed", "false");
    toggle.innerHTML = EYE_ICON;
    return toggle;
  }

  function enhancePasswordFields() {
    var fields = document.querySelectorAll('input[type="password"]');
    Array.prototype.forEach.call(fields, function (field) {
      if (!field.id || field.closest(".password-field")) return;

      var wrapper = document.createElement("div");
      wrapper.className = "password-field";
      field.parentNode.insertBefore(wrapper, field);
      wrapper.appendChild(field);
      wrapper.appendChild(buildToggle(field));
    });
  }

  function initPasswordToggles() {
    enhancePasswordFields();

    document.addEventListener("click", function (event) {
      var toggle = event.target.closest("[data-password-toggle]");
      if (!toggle) return;

      var field = document.getElementById(toggle.getAttribute("data-password-toggle"));
      if (!field) return;

      var isHidden = field.type === "password";
      field.type = isHidden ? "text" : "password";
      toggle.setAttribute("aria-pressed", String(isHidden));
      toggle.setAttribute("aria-label", isHidden ? "Hide password" : "Show password");
      toggle.innerHTML = isHidden ? EYE_OFF_ICON : EYE_ICON;
      field.focus();
    });
  }

  /* --- Word count for long-form editors ---------------------------------- */

  function initWordCounts() {
    var fields = document.querySelectorAll("[data-word-count]");
    if (!fields.length) return;

    function render(field) {
      var target = document.getElementById(field.getAttribute("data-word-count"));
      if (!target) return;
      var text = field.value.trim();
      var words = text ? text.split(/\s+/).length : 0;
      target.textContent = words === 1 ? "1 word" : words + " words";
    }

    fields.forEach(function (field) {
      render(field);
      field.addEventListener("input", function () {
        render(field);
      });
    });
  }

  function init() {
    initNavigation();
    initConfirmations();
    initSubmitStates();
    initDismissibleAlerts();
    initPasswordToggles();
    initWordCounts();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
