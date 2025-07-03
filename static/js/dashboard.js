function copier(id) {
    const input = document.getElementById("pw-" + id);
    input.select();
    input.setSelectionRange(0, 99999);
    document.execCommand("copy");

    const button = event.currentTarget;
    const originalIcon = button.innerHTML;
    button.innerHTML = '<i class="bi bi-check-lg text-success"></i>';
    setTimeout(() => {
        button.innerHTML = originalIcon;
    }, 1500);
}
function supprimerPassword(id, button) {
if (!confirm("Voulez-vous vraiment supprimer ce mot de passe ?")) return;

fetch(`/delete-password/${id}`, {
method: "DELETE"
})
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

document.addEventListener("DOMContentLoaded", () => {
const deleteButtons = document.querySelectorAll(".btn-delete-password");

deleteButtons.forEach(button => {
button.addEventListener("click", function () {
const id = this.getAttribute("data-id");

if (!confirm("❗ Voulez-vous vraiment supprimer ce mot de passe ?")) return;

fetch(`/delete-password/${id}`, {
    method: "DELETE"
})
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
});

