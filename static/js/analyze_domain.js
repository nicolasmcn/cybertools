fetch("/check-auth")
  .then(res => res.json())
  .then(data => {
    if (!data.authenticated) {
      window.location.href = "/login";
    }
  });

function analyserDomaine(e) {
    e.preventDefault();
    const domaine = document.getElementById("inputDomaine").value.trim();
    const resultatDiv = document.getElementById("resultatAnalyse");

    if (!domaine) {
        resultatDiv.innerHTML = `<div class="alert alert-warning">⚠️ Veuillez entrer un nom de domaine.</div>`;
        return;
    }

    resultatDiv.innerHTML = `<p>⏳ Analyse en cours...</p>`;

    fetch(`/analyze?domain=${encodeURIComponent(domaine)}`)
        .then(res => res.json())
        .then(data => {
            if (data.error) {
                resultatDiv.innerHTML = `<div class="alert alert-danger">❌ Erreur : ${data.error}</div>`;
                return;
            }

            const confiance = Math.round((data.score / data.score_max) * 100);
            const niveau = confiance >= 80 ? "Élevé" : confiance >= 50 ? "Moyen" : "Faible";
            const badge = confiance >= 80 ? "success" : confiance >= 50 ? "warning" : "danger";

            const positifs = [];
            const negatifs = [];

            if (data.domain_age_days > 180) positifs.push("Le nom de domaine est relativement ancien.");
            else negatifs.push("Le domaine est très récent.");

            if (data.ssl_valid) positifs.push("Un certificat SSL valide est détecté.");
            else negatifs.push("Aucun certificat SSL détecté.");

            if (data.https_accessible) positifs.push("Le site est accessible en HTTPS.");
            else negatifs.push("Le site ne semble pas disponible en HTTPS.");

            if (data.whois_private === "no") positifs.push("Les informations WHOIS sont publiques.");
            else negatifs.push("Le WHOIS est privé (propriétaire masqué).");

            if (data.cloudflare_protected === "Oui") positifs.push("Le site est protégé par Cloudflare.");
            else if (data.cloudflare_protected === "Non") negatifs.push("Pas de protection Cloudflare détectée.");

            if (data.malware_detected) {
                negatifs.push(`⚠️ Le site est signalé comme malveillant par : ${data.malware_engines.join(", ")}`);
            } else {
                positifs.push("✅ Aucun signalement de malware détecté.");
            }

            resultatDiv.innerHTML = `
                <div class="card p-4 shadow text-start">
                    <h4 class="mb-3">🔍 Analyse du site : <strong>${data.domain}</strong></h4>

                    ${data.malware_detected ? `
                        <div class="alert alert-danger fw-bold">
                            🚨 Attention : ce site est signalé comme malveillant !
                            <br><small>Moteurs : ${data.malware_engines.join(", ")}</small>
                        </div>` : ""}

                    <div class="d-flex align-items-center gap-3 mb-3">
                        <div class="progress" style="width: 100px; height: 20px;">
                            <div class="progress-bar bg-${badge}" role="progressbar" style="width: ${confiance}%;">${confiance}%</div>
                        </div>
                        <span class="badge bg-${badge}">${niveau}</span>
                    </div>

                    <p><strong>🛰️ Adresse IP :</strong> ${data.ip_address || "Inconnue"}</p>
                    <p><strong>🔁 Reverse DNS :</strong> ${data.reverse_dns || "Inconnu"}</p>
                    <p><strong>📆 Expiration :</strong> ${data.domain_expiration || "Non disponible"}</p>
                    <p><strong>🏢 Registrar :</strong> ${data.registrar || "Inconnu"}</p>

                    <div class="row mt-4">
                        <div class="col-md-6">
                            <h5 class="text-success">✔ Points positifs</h5>
                            <ul class="list-group list-group-flush">
                                ${positifs.map(p => `<li class="list-group-item">${p}</li>`).join("")}
                            </ul>
                        </div>
                        <div class="col-md-6">
                            <h5 class="text-danger">❌ Points négatifs</h5>
                            <ul class="list-group list-group-flush">
                                ${negatifs.map(n => `<li class="list-group-item">${n}</li>`).join("")}
                            </ul>
                        </div>
                    </div>
                </div>`;
        })
        .catch(err => {
            resultatDiv.innerHTML = `<div class="alert alert-danger">⚠️ Erreur serveur : ${err.message}</div>`;
        });
}