// ===========================
// TEST DE ROBUSTESSE
// ===========================
function verifierRobustesse() {
    const password = document.getElementById("passwordInput").value;
    const resultDiv = document.getElementById("passwordResult");

    if (!password) {
        resultDiv.innerHTML = `<p class="text-muted">⚠️ Entrez un mot de passe pour voir son niveau de sécurité.</p>`;
        return;
    }

    let score = 0;
    let feedback = [];

    if (password.length >= 12) score++;
    else feedback.push("🔸 Longueur trop courte (< 12 caractères)");

    if (/[a-z]/.test(password)) score++;
    else feedback.push("🔸 Ajouter des lettres minuscules");

    if (/[A-Z]/.test(password)) score++;
    else feedback.push("🔸 Ajouter des lettres majuscules");

    if (/[0-9]/.test(password)) score++;
    else feedback.push("🔸 Ajouter des chiffres");

    if (/[^A-Za-z0-9]/.test(password)) score++;
    else feedback.push("🔸 Ajouter des symboles spéciaux (@, %, #...)");

    const niveaux = ["🚫 Très faible", "⚠️ Faible", "😐 Moyen", "✅ Fort", "🔒 Très fort"];
    const couleurs = ["danger", "danger", "warning", "success", "primary"];
    const barre = ["20%", "40%", "60%", "80%", "100%"];

    resultDiv.innerHTML = `
        <div class="progress mb-2" style="height: 20px;">
            <div class="progress-bar bg-${couleurs[score]}" style="width: ${barre[score]};">
                ${niveaux[score]}
            </div>
        </div>
        ${feedback.length
            ? `<p class="text-danger mt-2">Conseils :<br>• ${feedback.join("<br>• ")}</p>`
            : `<p class="text-success mt-2">Parfait, ce mot de passe est robuste 💪</p>`}
    `;
}


// ===========================
// GÉNÉRATION + SAUVEGARDE
// ===========================
function genererMotDePasse() {
    const length = parseInt(document.getElementById("passwordLength").value);
    const useLower = document.getElementById("includeLower").checked;
    const useUpper = document.getElementById("includeUpper").checked;
    const useNumbers = document.getElementById("includeNumbers").checked;
    const useSymbols = document.getElementById("includeSymbols").checked;

    const resultField = document.getElementById("resultPassword");
    const statusDiv = document.getElementById("saveStatus");

    const lowercase = "abcdefghijklmnopqrstuvwxyz";
    const uppercase = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
    const numbers = "0123456789";
    const symbols = "!@#$%^&*()-_=+[]{}<>?/";

    let pool = "";
    if (useLower) pool += lowercase;
    if (useUpper) pool += uppercase;
    if (useNumbers) pool += numbers;
    if (useSymbols) pool += symbols;

    if (!pool.length) {
        resultField.value = "⚠️ Sélectionne au moins un critère";
        return;
    }

    let password = "";
    for (let i = 0; i < length; i++) {
        password += pool.charAt(Math.floor(Math.random() * pool.length));
    }

    resultField.value = password;

    statusDiv.innerHTML = "<div class='alert alert-info'>⏳ Sauvegarde en cours...</div>";

    fetch("/check-auth", { cache: "no-store" })
    .then(res => res.json())
        .then(auth => {
            if (!auth.authenticated) {
                statusDiv.innerHTML =
                    "<div class='alert alert-warning'>🔒 Connecte-toi pour sauvegarder le mot de passe</div>";
                return;
            }

            fetch("/save-password", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    password: password,
                    strength: "Auto"
                })
            })
            .then(res => res.json())
            .then(response => {
                if (response.success) {
                    statusDiv.innerHTML =
                        "<div class='alert alert-success'>✅ Mot de passe sauvegardé dans votre dashboard</div>";
                } else {
                    statusDiv.innerHTML =
                        "<div class='alert alert-danger'>❌ Échec de sauvegarde</div>";
                }
            })
            .catch(() => {
                statusDiv.innerHTML =
                    "<div class='alert alert-danger'>❌ Erreur serveur</div>";
            });
        });
}



// ===========================
// COPIER MOT DE PASSE
// ===========================
function copierMotDePasse() {
    const resultField = document.getElementById("resultPassword");

    if (!resultField.value) return;

    resultField.select();
    document.execCommand("copy");

    alert("📋 Mot de passe copié dans le presse-papier.");
}
