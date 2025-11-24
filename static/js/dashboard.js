"use strict";

/* =========================
   ÉTAT GLOBAL
   ========================= */
let pendingTargetId = null;       
let pendingAction = null;         
let revealTimeoutMs = 30000;      
let reauthModalInstance = null;

/* =========================
   OUTILS
   ========================= */
function getInput(id) {
  return document.getElementById(id);
}

function updateEyeIcon(targetId, show) {
  document
    .querySelectorAll(`.btn-eye[data-target="${targetId}"] i`)
    .forEach(i => {
      if (show) { i.classList.remove("bi-eye"); i.classList.add("bi-eye-slash"); }
      else { i.classList.add("bi-eye"); i.classList.remove("bi-eye-slash"); }
    });
}

function copyInputValue(input, button) {
  const doFeedback = () => {
    if (!button && typeof event !== "undefined") button = event.currentTarget;
    if (button) {
      const originalIcon = button.innerHTML;
      button.innerHTML = '<i class="bi bi-check-lg text-success"></i>';
      setTimeout(() => { button.innerHTML = originalIcon; }, 1500);
    } else {
      alert("📋 Copié.");
    }
  };

  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(input.value).then(doFeedback).catch(() => {
      input.removeAttribute("readonly");
      input.select();
      input.setSelectionRange(0, 99999);
      document.execCommand("copy");
      input.setAttribute("readonly", "readonly");
      doFeedback();
    });
  } else {
    input.removeAttribute("readonly");
    input.select();
    input.setSelectionRange(0, 99999);
    document.execCommand("copy");
    input.setAttribute("readonly", "readonly");
    doFeedback();
  }
}

function maskAfterDelay(targetId) {
  const input = getInput(targetId);
  if (!input) return;
  setTimeout(() => {
    if (input.type === "text") {
      input.type = "password";
      updateEyeIcon(targetId, false);
    }
  }, revealTimeoutMs);
}

/* =========================
   MODAL RE-AUTH
   ========================= */
function openReauthModal() {
  const modalEl = document.getElementById("confirmViewModal");
  const field = document.getElementById("accountPassword");

  if (!modalEl || !field) {
    const pwd = prompt("Mot de passe du compte :");
    if (pwd !== null) submitReauth(pwd);
    return;
  }

  field.value = "";
  field.classList.remove("is-invalid");

  if (!reauthModalInstance && window.bootstrap) {
    reauthModalInstance = new bootstrap.Modal(modalEl);
  }
  reauthModalInstance?.show();
}

async function submitReauth(pwd) {
  try {
    const res = await fetch("/re-auth", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ password: pwd })
    });
    const data = await res.json().catch(() => ({}));
    if (!(res.ok && data.valid)) throw new Error("invalid");

    if (reauthModalInstance) reauthModalInstance.hide();

    if (!pendingTargetId) return;
    const input = getInput(pendingTargetId);
    if (!input) return;

    if (pendingAction === "reveal") {
      input.type = "text";
      updateEyeIcon(pendingTargetId, true);
      maskAfterDelay(pendingTargetId);
    } else if (pendingAction === "copy") {
      copyInputValue(input);
    }
  } catch (e) {
    const f = document.getElementById("accountPassword");
    if (f) {
      f.classList.add("is-invalid");
      setTimeout(() => f.classList.remove("is-invalid"), 1500);
    } else {
      alert("Mot de passe incorrect.");
    }
  } finally {
    pendingTargetId = null;
    pendingAction = null;
  }
}

/* =========================
   ACTIONS LIGNE
   ========================= */
function copier(id, button) {
  const input = getInput("pw-" + id);
  if (!input) return;

  if (input.type === "password") {
    pendingTargetId = "pw-" + id;
    pendingAction = "copy";
    openReauthModal();
    return;
  }
  copyInputValue(input, button);
}

function handleEyeClick(btn) {
  const targetId = btn.dataset.target;
  const input = getInput(targetId);
  if (!input) return;

  if (input.type === "text") {
    input.type = "password";
    updateEyeIcon(targetId, false);
  } else {
    pendingTargetId = targetId;
    pendingAction = "reveal";
    openReauthModal();
  }
}

/* =========================
   SUPPRESSION
   ========================= */
function supprimerPassword(id, button) {
  if (!confirm("Voulez-vous vraiment supprimer ce mot de passe ?")) return;

  fetch(`/delete-password/${id}`, { method: "DELETE" })
    .then(response => {
      if (response.ok) {
        const row = button.closest("tr");
        row.remove();
      } else {
        alert("Erreur lors de la suppression.");
      }
    })
    .catch(error => {
      alert("Erreur réseau.");
      console.error(error);
    });
}

/* =========================
   BIND AU CHARGEMENT
   ========================= */
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".btn-delete-password").forEach(button => {
    button.addEventListener("click", function () {
      const id = this.getAttribute("data-id");
      if (!confirm("❗ Voulez-vous vraiment supprimer ce mot de passe ?")) return;

      fetch(`/delete-password/${id}`, { method: "DELETE" })
        .then(response => {
          if (response.ok) {
            this.closest("tr").remove();
          } else {
            alert("Erreur lors de la suppression.");
            console.warn("Erreur HTTP:", response.status);
          }
        })
        .catch(error => {
          alert("Erreur réseau.");
          console.error("Erreur fetch:", error);
        });
    });
  });

  document.querySelectorAll(".btn-eye").forEach(btn => {
    btn.addEventListener("click", () => handleEyeClick(btn));
  });

  document.querySelectorAll(".btn-copy").forEach(btn => {
    btn.addEventListener("click", () => {
      const targetId = btn.dataset.target || btn.getAttribute("data-target");
      const input = targetId ? getInput(targetId) : null;
      if (!input) return;

      if (input.type === "password") {
        pendingTargetId = targetId;
        pendingAction = "copy";
        openReauthModal();
      } else {
        copyInputValue(input, btn);
      }
    });
  });

  document.getElementById("confirmViewForm")?.addEventListener("submit", (e) => {
    e.preventDefault();
    const pwd = document.getElementById("accountPassword")?.value.trim() || "";
    submitReauth(pwd);
  });
});