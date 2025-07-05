function verifierRobustesse() {
    const password = document.getElementById("passwordInput").value;
    const resultDiv = document.getElementById("passwordResult");

    if (!password) {
        resultDiv.innerHTML = `<p class="text-muted">⚠️ Entrez un mot de passe pour voir son niveau de sécurité.</p>`;
        return;
    }

    let score = 0;
    let feedback = [];

    if (password.length >= 8) score++;
    else feedback.push("🔸 Longueur trop courte (< 8 caractères)");

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
        ${feedback.length ? `<p class="text-danger mt-2">Conseils :<br>• ${feedback.join("<br>• ")}</p>` : `<p class="text-success mt-2">Parfait, ce mot de passe est robuste 💪</p>`}
    `;
}

function genererMotDePasse() {
    const length = parseInt(document.getElementById("passwordLength").value);
    const useLower = document.getElementById("includeLower").checked;
    const useUpper = document.getElementById("includeUpper").checked;
    const useNumbers = document.getElementById("includeNumbers").checked;
    const useSymbols = document.getElementById("includeSymbols").checked;
    const resultField = document.getElementById("resultPassword");

    const lowercase = "abcdefghijklmnopqrstuvwxyz";
    const uppercase = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
    const numbers = "0123456789";
    const symbols = "!@#$%^&*()-_=+[]{}<>?/";

    let pool = "";
    if (useLower) pool += lowercase;
    if (useUpper) pool += uppercase;
    if (useNumbers) pool += numbers;
    if (useSymbols) pool += symbols;

    if (pool.length === 0) {
        resultField.value = "⚠️ Aucun critère sélectionné";
        return;
    }

    let password = "";
    for (let i = 0; i < length; i++) {
        password += pool[Math.floor(Math.random() * pool.length)];
    }

    resultField.value = password;

    // 🔐 Si connecté, envoie vers le backend pour sauvegarde
    fetch('/check-auth')
        .then(res => res.json())
        .then(data => {
            if (data.authenticated) {
                fetch("/save-password", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        password: password,
                        strength: "Auto"
                    })
                })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        alert("✅ Mot de passe sauvegardé dans votre tableau.");
                    }
                });
            }
        });
}

function copierMotDePasse() {
    const resultField = document.getElementById("resultPassword");
    resultField.select();
    document.execCommand("copy");
    alert("📋 Mot de passe copié dans le presse-papier.");
} 