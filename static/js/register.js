document.getElementById("login_password").addEventListener("input", function() {
    const pw = this.value;
    const feedback = document.getElementById("passwordFeedback");

    let errors = [];

    if (pw.length < 8) errors.push("Au moins 8 caractères");
    if (!/\d/.test(pw)) errors.push("Au moins 1 chiffre");
    if (!/[!@#$%^&*]/.test(pw)) errors.push("1 caractère spécial");

    feedback.innerHTML = errors.length 
        ? "Mot de passe faible :<br>" + errors.join("<br>")
        : "<span class='text-success'>Mot de passe valide ✅</span>";
});
