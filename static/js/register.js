document.addEventListener("DOMContentLoaded", () => {

    const passwordInput = document.getElementById("login_password");
    const feedback = document.getElementById("passwordFeedback");
    const toggleBtn = document.querySelector(".pw-toggle-btn");
    const icon = toggleBtn.querySelector("i");

    // 👁️ AFFICHER / CACHER MOT DE PASSE
    toggleBtn.addEventListener("click", () => {
        if (passwordInput.type === "password") {
            passwordInput.type = "text";
            icon.classList.replace("bi-eye", "bi-eye-slash");
        } else {
            passwordInput.type = "password";
            icon.classList.replace("bi-eye-slash", "bi-eye");
        }
    });

    passwordInput.addEventListener("input", function() {
        const pw = this.value;
        let errors = [];

        if (pw.length < 12) errors.push("• 12 caractères minimum");
        if (!/[A-Z]/.test(pw)) errors.push("• 1 majuscule");
        if (!/[0-9]/.test(pw)) errors.push("• 1 chiffre");
        if (!/[!@#$%^&*(),.?\":{}|<>]/.test(pw)) errors.push("• 1 caractère spécial");

        if (pw.length === 0) {
            feedback.innerHTML = "";
            return;
        }

        if (errors.length === 0) {
            feedback.innerHTML = `
                <span class="text-success fw-bold">
                    ✅ Mot de passe suffisamment sécurisé pour l'enregistrement
                </span>`;
        } else {
            feedback.innerHTML = `
                <span class="text-danger">
                    Mot de passe requis :<br>${errors.join("<br>")}
                </span>`;
        }
    });

});
