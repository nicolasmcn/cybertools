function verifierMotDePasse() {
    const password = document.getElementById("password").value;
    const feedback = document.getElementById("feedback");

    let erreurs = [];

    if (password.length < 8) {
        erreurs.push("• Au moins 8 caractères");
    }

    const chiffres = password.match(/\d/g) || [];
    if (chiffres.length < 2) {
        erreurs.push("• Au moins 2 chiffres");
    }

    if (!/[^\w]/.test(password)) {
        erreurs.push("• Au moins un caractère spécial (@, #, !, etc.)");
    }

    if (erreurs.length > 0) {
        feedback.innerHTML = "Mot de passe trop faible :<br>" + erreurs.join("<br>");
    } else {
        feedback.innerHTML = "<span class='text-success'>Mot de passe conforme ✅</span>";
    }
}