"use strict";

/* =========================
   ÉTAT GLOBAL
   ========================= */
let pendingTargetId = null;       // ex: "pw-42"
let pendingAction = null;         // "reveal" | "copy"
let revealTimeoutMs = 30000;      // remasquer après 30s
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

  // Méthode moderne si dispo
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(input.value).then(doFeedback).catch(() => {
      // fallback si refus/erreur
      input.removeAttribute("readonly");
      input.select();
      input.setSelectionRange(0, 99999);
      document.execCommand("copy");
      input.setAttribute("readonly", "readonly");
      doFeedback();
    });
  } else {
    // fallback legacy
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
    // Fallback si modal absent : prompt()
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
      // ✅ Révéler tout de suite, remasquer après X s
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
// Compat avec onclick="copier('ID', this)"
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
    // déjà visible -> remasquer
    input.type = "password";
    updateEyeIcon(targetId, false);
  } else {
    // masqué -> re-auth, puis révéler
    pendingTargetId = targetId;
    pendingAction = "reveal";
    openReauthModal();
  }
}

/* =========================
   SUPPRESSION (inchangé)
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
  // Boutons supprimer (déjà dans ton code)
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

  // Boutons œil (révéler/masquer avec re-auth)
  document.querySelectorAll(".btn-eye").forEach(btn => {
    btn.addEventListener("click", () => handleEyeClick(btn));
  });

  // Boutons copier (au cas où tu retires l'attribut onclick côté HTML)
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

  // Soumission du modal
  document.getElementById("confirmViewForm")?.addEventListener("submit", (e) => {
    e.preventDefault();
    const pwd = document.getElementById("accountPassword")?.value.trim() || "";
    submitReauth(pwd);
  });
});