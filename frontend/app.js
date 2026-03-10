const API = "";

// --- Theme toggle ---
const themeToggle = document.getElementById("theme-toggle");
const htmlEl = document.documentElement;

function applyTheme(theme) {
    htmlEl.setAttribute("data-theme", theme);
    themeToggle.textContent = theme === "dark" ? "☀️" : "🌙";
    localStorage.setItem("theme", theme);
}

// Init from localStorage or default dark
applyTheme(localStorage.getItem("theme") || "dark");

themeToggle.addEventListener("click", () => {
    const current = htmlEl.getAttribute("data-theme");
    applyTheme(current === "dark" ? "light" : "dark");
});

// --- Cache pour résolution noms ---
let clientsCache = {};
let vehiculesCache = {};

// --- Utilitaires ---
function fmt(n) {
    return (n || 0).toLocaleString("fr-FR", { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + " \u20ac";
}

function esc(s) {
    if (!s) return "";
    const d = document.createElement("div");
    d.textContent = s;
    return d.innerHTML;
}

// --- Tabs ---
document.querySelectorAll(".tab-link").forEach(link => {
    link.addEventListener("click", e => {
        e.preventDefault();
        document.querySelectorAll(".tab-link").forEach(l => l.classList.remove("active"));
        document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));
        link.classList.add("active");
        const tab = link.dataset.tab;
        document.getElementById("tab-" + tab).classList.add("active");
        loadTab(tab);
    });
});

function loadTab(tab) {
    if (tab === "factures") loadFactures();
    else if (tab === "clients") loadClients();
    else if (tab === "vehicules") loadVehicules();
}

// --- Upload ---
const uploadZone = document.getElementById("upload-zone");
const fileInput = document.getElementById("file-input");
const btnSelect = document.getElementById("btn-select");
const btnUpload = document.getElementById("btn-upload");
const fileList = document.getElementById("file-list");
let selectedFiles = [];

btnSelect.addEventListener("click", () => fileInput.click());

fileInput.addEventListener("change", () => {
    selectedFiles = Array.from(fileInput.files);
    renderFileList();
});

uploadZone.addEventListener("dragover", e => {
    e.preventDefault();
    uploadZone.classList.add("dragover");
});

uploadZone.addEventListener("dragleave", () => {
    uploadZone.classList.remove("dragover");
});

uploadZone.addEventListener("drop", e => {
    e.preventDefault();
    uploadZone.classList.remove("dragover");
    selectedFiles = Array.from(e.dataTransfer.files).filter(f => f.name.toLowerCase().endsWith(".pdf"));
    renderFileList();
});

function renderFileList() {
    fileList.innerHTML = selectedFiles.map(f => `<span class="file-item">${esc(f.name)}</span>`).join("");
    btnUpload.hidden = selectedFiles.length === 0;
}

btnUpload.addEventListener("click", async () => {
    if (selectedFiles.length === 0) return;

    const progress = document.getElementById("upload-progress");
    const resultsDiv = document.getElementById("upload-results");
    progress.hidden = false;
    resultsDiv.hidden = true;
    btnUpload.disabled = true;

    const formData = new FormData();
    selectedFiles.forEach(f => formData.append("files", f));

    try {
        const res = await fetch(API + "/api/upload", { method: "POST", body: formData });
        const data = await res.json();

        progress.hidden = true;
        resultsDiv.hidden = false;
        resultsDiv.innerHTML = data.results.map(r => {
            if (r.status === "success") {
                return `<p class="result-success">OK : ${esc(r.pdf_filename)} (${r.action})</p>`;
            } else {
                return `<p class="result-error">Erreur : ${esc(r.pdf_filename)} - ${esc(r.message)}</p>`;
            }
        }).join("");

        // Rafraîchir les données
        selectedFiles = [];
        fileInput.value = "";
        renderFileList();
        loadFactures();
    } catch (err) {
        progress.hidden = true;
        resultsDiv.hidden = false;
        resultsDiv.innerHTML = `<p class="result-error">Erreur : ${esc(err.message)}</p>`;
    } finally {
        btnUpload.disabled = false;
    }
});

// --- Chargement Factures ---
async function loadFactures() {
    // Charger stats
    const statsRes = await fetch(API + "/api/factures/stats");
    const stats = await statsRes.json();
    document.getElementById("stat-ht").textContent = fmt(stats.total_ht);
    document.getElementById("stat-tva").textContent = fmt(stats.total_tva);
    document.getElementById("stat-nb").textContent = stats.nb_factures;

    // Charger caches pour résolution noms
    await refreshCaches();

    // Charger factures
    const res = await fetch(API + "/api/factures");
    const factures = await res.json();

    const tbody = document.getElementById("factures-body");
    tbody.innerHTML = factures.map(f => `
        <tr>
            <td>${esc(f.numero_facture)}</td>
            <td>${esc(f.date_facture)}</td>
            <td>${esc(clientsCache[f.client_id]?.nom || "—")}</td>
            <td>${esc(vehiculesCache[f.vehicule_id]?.immatriculation || "—")}</td>
            <td>${fmt(f.total_ht)}</td>
            <td>${fmt(f.montant_tva)}</td>
            <td>${fmt(f.total_ttc)}</td>
            <td>
                <button class="btn-detail" onclick="showFactureDetail('${f.id}')">Voir</button>
                <button class="btn-delete" onclick="deleteFacture('${f.id}')">Suppr.</button>
            </td>
        </tr>
    `).join("");
}

// --- Chargement Clients ---
async function loadClients() {
    const res = await fetch(API + "/api/clients");
    const clients = await res.json();

    const tbody = document.getElementById("clients-body");
    tbody.innerHTML = clients.map(c => `
        <tr>
            <td>${esc(c.nom)}</td>
            <td>${esc(c.adresse)}</td>
            <td>${esc(c.telephone)}</td>
            <td>${esc(c.email)}</td>
            <td>
                <button class="btn-edit" onclick="editClient('${c.id}')">Editer</button>
                <button class="btn-delete" onclick="deleteClient('${c.id}')">Suppr.</button>
            </td>
        </tr>
    `).join("");
}

// --- Chargement Véhicules ---
async function loadVehicules() {
    await refreshCaches();

    const res = await fetch(API + "/api/vehicules");
    const vehicules = await res.json();

    const tbody = document.getElementById("vehicules-body");
    tbody.innerHTML = vehicules.map(v => `
        <tr>
            <td>${esc(v.immatriculation)}</td>
            <td>${esc(v.marque)}</td>
            <td>${esc(v.modele)}</td>
            <td>${esc(clientsCache[v.client_id]?.nom || "—")}</td>
            <td>${v.annee || "—"}</td>
            <td>${v.kilometrage ? v.kilometrage.toLocaleString("fr-FR") + " km" : "—"}</td>
            <td>
                <button class="btn-edit" onclick="editVehicule('${v.id}')">Editer</button>
                <button class="btn-delete" onclick="deleteVehicule('${v.id}')">Suppr.</button>
            </td>
        </tr>
    `).join("");
}

// --- Caches ---
async function refreshCaches() {
    const [clientsRes, vehiculesRes] = await Promise.all([
        fetch(API + "/api/clients"),
        fetch(API + "/api/vehicules"),
    ]);
    const clients = await clientsRes.json();
    const vehicules = await vehiculesRes.json();

    clientsCache = {};
    clients.forEach(c => clientsCache[c.id] = c);
    vehiculesCache = {};
    vehicules.forEach(v => vehiculesCache[v.id] = v);
}

// --- Détail facture ---
async function showFactureDetail(id) {
    const [res, imagesRes] = await Promise.all([
        fetch(API + "/api/factures/" + id),
        fetch(API + "/api/factures/" + id + "/images"),
    ]);
    const f = await res.json();
    const imageUrls = await imagesRes.json();
    await refreshCaches();

    const modal = document.getElementById("facture-modal");
    document.getElementById("modal-title").textContent = "Facture " + f.numero_facture;

    const imagesHtml = imageUrls.length > 0
        ? `<div class="facture-images">
            <h4>Document original</h4>
            ${imageUrls.map((url, i) => `<img src="${url}" alt="Page ${i + 1}" class="facture-page-img">`).join("")}
           </div>`
        : "";

    document.getElementById("modal-body").innerHTML = `
        <p><strong>Date :</strong> ${esc(f.date_facture)}</p>
        <p><strong>Client :</strong> ${esc(clientsCache[f.client_id]?.nom || "—")}</p>
        <p><strong>Véhicule :</strong> ${esc(vehiculesCache[f.vehicule_id]?.immatriculation || "—")}
            (${esc(vehiculesCache[f.vehicule_id]?.marque || "")} ${esc(vehiculesCache[f.vehicule_id]?.modele || "")})</p>
        <p><strong>Fichier :</strong> ${esc(f.pdf_filename)}</p>
        <table>
            <thead>
                <tr><th>Description</th><th>Qté</th><th>PU HT</th><th>Montant HT</th><th>Type</th></tr>
            </thead>
            <tbody>
                ${(f.lignes || []).map(l => `
                    <tr>
                        <td>${esc(l.description)}</td>
                        <td>${l.quantite}</td>
                        <td>${fmt(l.prix_unitaire_ht)}</td>
                        <td>${fmt(l.montant_ht)}</td>
                        <td>${esc(l.type)}</td>
                    </tr>
                `).join("")}
            </tbody>
        </table>
        <p><strong>Total HT :</strong> ${fmt(f.total_ht)}</p>
        <p><strong>TVA (${f.tva_taux}%) :</strong> ${fmt(f.montant_tva)}</p>
        <p><strong>Total TTC :</strong> ${fmt(f.total_ttc)}</p>
        ${imagesHtml}
    `;
    modal.showModal();

    modal.querySelector(".close-modal").onclick = () => modal.close();
    modal.addEventListener("click", e => { if (e.target === modal) modal.close(); }, { once: true });
}

// --- Edition ---
function openEditModal(title, fields, onSave) {
    const modal = document.getElementById("edit-modal");
    document.getElementById("edit-modal-title").textContent = title;
    const form = document.getElementById("edit-form");
    form.innerHTML = fields.map(f => `
        <label>
            ${esc(f.label)}
            <input type="${f.type || 'text'}" name="${f.name}" value="${esc(f.value || '')}" placeholder="${esc(f.label)}">
        </label>
    `).join("");

    modal.showModal();

    const closeModal = () => modal.close();
    modal.querySelector(".close-edit-modal").onclick = closeModal;
    modal.querySelector(".close-edit-modal-btn").onclick = (e) => { e.preventDefault(); closeModal(); };

    document.getElementById("edit-save-btn").onclick = async (e) => {
        e.preventDefault();
        const data = {};
        fields.forEach(f => {
            const val = form.querySelector(`[name="${f.name}"]`).value;
            data[f.name] = val || null;
        });
        await onSave(data);
        closeModal();
    };
}

async function editClient(id) {
    const res = await fetch(API + "/api/clients/" + id);
    const c = await res.json();

    openEditModal("Modifier client", [
        { name: "nom", label: "Nom", value: c.nom },
        { name: "adresse", label: "Adresse", value: c.adresse },
        { name: "telephone", label: "Téléphone", value: c.telephone },
        { name: "email", label: "Email", value: c.email },
    ], async (data) => {
        await fetch(API + "/api/clients/" + id, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data),
        });
        loadClients();
    });
}

async function editVehicule(id) {
    const res = await fetch(API + "/api/vehicules/" + id);
    const v = await res.json();

    openEditModal("Modifier véhicule", [
        { name: "marque", label: "Marque", value: v.marque },
        { name: "modele", label: "Modèle", value: v.modele },
        { name: "immatriculation", label: "Immatriculation", value: v.immatriculation },
        { name: "vin", label: "VIN", value: v.vin },
        { name: "annee", label: "Année", type: "number", value: v.annee },
        { name: "kilometrage", label: "Kilométrage", type: "number", value: v.kilometrage },
    ], async (data) => {
        if (data.annee) data.annee = parseInt(data.annee);
        if (data.kilometrage) data.kilometrage = parseInt(data.kilometrage);
        await fetch(API + "/api/vehicules/" + id, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data),
        });
        loadVehicules();
    });
}

// --- Suppressions ---
async function deleteFacture(id) {
    if (!confirm("Supprimer cette facture ?")) return;
    await fetch(API + "/api/factures/" + id, { method: "DELETE" });
    loadFactures();
}

async function deleteClient(id) {
    if (!confirm("Supprimer ce client ?")) return;
    await fetch(API + "/api/clients/" + id, { method: "DELETE" });
    loadClients();
}

async function deleteVehicule(id) {
    if (!confirm("Supprimer ce véhicule ?")) return;
    await fetch(API + "/api/vehicules/" + id, { method: "DELETE" });
    loadVehicules();
}

// --- Init ---
loadFactures();
