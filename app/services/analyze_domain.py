import whois
import ssl
import socket
import datetime
import requests


VT_API_KEY = "5baf850bbdda196e250b370752169d94eb4ffd24cd3b0ae3615df28da95a4719"

def calculate_score(data):
    total = 0
    max_score = 100
    points = []

    def add(condition, pts, label):
        nonlocal total
        earned = pts if condition else 0
        total += earned
        points.append({"critere": label, "points": earned, "max": pts})

    add(data["ssl_valid"], 10, "Certificat SSL valide")
    add(data["https_accessible"], 10, "HTTPS accessible")
    add(data["domain_age_days"] > 365, 10, "Domaine > 1 an")
    add(data["whois_private"] == "no", 5, "WHOIS public")
    
    try:
        expire_date = datetime.datetime.strptime(data["domain_expiration"], "%Y-%m-%d %H:%M:%S")
        add(expire_date > datetime.datetime.now() + datetime.timedelta(days=90), 5, "Expiration > 3 mois")
    except:
        add(False, 5, "Expiration > 3 mois")

    add(data["ip_address"] != "Non résolu", 5, "IP résolue")
    add(data["reverse_dns"] != "Inconnu", 5, "Reverse DNS résolu")
    add(data["registrar"] != "Inconnu", 5, "Registrar connu")
    add(data["cloudflare_protected"] == "Oui", 5, "Protection Cloudflare")
    add(not data["malware_detected"], 30, "Aucun malware détecté")

    return {
        "score": total,
        "score_max": max_score,
        "risk_level": "Élevé" if total >= 80 else "Moyen" if total >= 50 else "Faible",
        "note_details": points
    }

def check_ssl(domain):
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                return True, cert['notAfter']
    except Exception as e:
        return False, str(e)

def check_https(domain):
    try:
        r = requests.get(f"https://{domain}", timeout=5)
        return r.status_code == 200
    except:
        return False

def get_domain_info(domain):
    try:
        w = whois.whois(domain)
        creation_date = w.creation_date
        expiration_date = w.expiration_date
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
        if isinstance(expiration_date, list):
            expiration_date = expiration_date[0]
        age = (datetime.datetime.now() - creation_date).days if creation_date else -1
        registrar = w.registrar if w.registrar else "Inconnu"
        is_private = "yes" if "Privacy" in str(w.org) or "WhoisGuard" in str(w.org) else "no"
        return age, expiration_date, registrar, is_private
    except Exception:
        return -1, "Inconnue", "Inconnu", "inconnu"

def resolve_ip(domain):
    try:
        return socket.gethostbyname(domain)
    except:
        return "Non résolu"

def reverse_dns(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except:
        return "Inconnu"

def detect_cloudflare(domain):
    try:
        r = requests.get(f"http://{domain}", timeout=5)
        server = r.headers.get("Server", "")
        if "cloudflare" in server.lower():
            return "Oui"
        return "Non"
    except:
        return "Inconnu"

def check_virustotal(domain):
    try:
        url = f"https://www.virustotal.com/api/v3/domains/{domain}"
        headers = { "x-apikey": VT_API_KEY }
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            return {"malware_detected": False, "engines": [], "raw": "Non disponible"}

        data = r.json()
        stats = data["data"]["attributes"]["last_analysis_stats"]
        detected = stats["malicious"] > 0 or stats["suspicious"] > 0

        engines = []
        for engine, result in data["data"]["attributes"]["last_analysis_results"].items():
            if result["category"] in ["malicious", "suspicious"]:
                engines.append(engine)

        return {
            "malware_detected": detected,
            "engines": engines,
            "raw": stats
        }
    except Exception as e:
        return {"malware_detected": False, "engines": [], "raw": str(e)}

def analyze(domain):
    ip_address = resolve_ip(domain)
    reverse = reverse_dns(ip_address) if ip_address != "Non résolu" else "Inconnu"
    ssl_ok, ssl_info = check_ssl(domain)
    https_ok = check_https(domain)
    age, expiration, registrar, is_private = get_domain_info(domain)
    is_protected = detect_cloudflare(domain)
    vt_result = check_virustotal(domain)

    scoring = calculate_score({
        "ssl_valid": ssl_ok,
        "https_accessible": https_ok,
        "domain_age_days": age,
        "whois_private": is_private,
        "domain_expiration": expiration,
        "ip_address": ip_address,
        "reverse_dns": reverse,
        "registrar": registrar,
        "cloudflare_protected": is_protected,
        "malware_detected": vt_result["malware_detected"]
    })


    if vt_result["malware_detected"]:
        score = 0

    return {
        "domain": domain,
        "ip_address": ip_address,
        "reverse_dns": reverse,
        "cloudflare_protected": is_protected,
        "ssl_valid": ssl_ok,
        "ssl_info": ssl_info,
        "https_accessible": https_ok,
        "domain_age_days": age,
        "domain_expiration": str(expiration),
        "registrar": registrar,
        "whois_private": is_private,
        "malware_detected": vt_result["malware_detected"],
        "malware_engines": vt_result["engines"],
        "score": scoring["score"],
        "score_max": scoring["score_max"],
        "risk_level": scoring["risk_level"],
        "note_details": scoring["note_details"]
    }


# Test rapide en console
if __name__ == "__main__":
    domaine = input("Entrez un nom de domaine : ")
    result = analyze(domaine)
    print(result)
