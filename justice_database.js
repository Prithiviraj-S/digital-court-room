document.getElementById("caseForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const caseType = document.getElementById("caseType").value;
    const plaintiff = document.getElementById("plaintiff").value;
    const defendant = document.getElementById("defendant").value;
    const description = document.getElementById("description").value;

    const response = await fetch("http://localhost:5000/cases", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            caseType,
            plaintiff,
            defendant,
            description
        })
    });

    const data = await response.json();
    alert(data.message || data.error);

    document.getElementById("caseForm").reset();
    loadCases();
});


async function loadCases() {
    const response = await fetch("http://localhost:5000/cases");
    const cases = await response.json();

    const caseList = document.getElementById("caseList");
    caseList.innerHTML = "";

    cases.forEach(c => {
        const div = document.createElement("div");
        div.className = "case-item";
        div.innerHTML = `
            <div class="case-item-header">
                <span class="case-id">CASE #${c.id}</span>
                <span class="case-status status-pending">${c.status}</span>
            </div>
            <p><strong>${c.caseType}</strong></p>
            <p>Plaintiff: ${c.plaintiff}</p>
            <p>Defendant: ${c.defendant}</p>
            <button onclick="viewCase(${c.id})">View Details</button>
        `;
        caseList.appendChild(div);
    });
}


async function viewCase(id) {
    const response = await fetch(`http://localhost:5000/cases/${id}`);
    const c = await response.json();

    document.getElementById("detailsContent").innerHTML = `
        <p><strong>Case Type:</strong> ${c.caseType}</p>
        <p><strong>Plaintiff:</strong> ${c.plaintiff}</p>
        <p><strong>Defendant:</strong> ${c.defendant}</p>
        <p><strong>Description:</strong> ${c.description}</p>
        <p><strong>Status:</strong> ${c.status}</p>
    `;

    document.getElementById("caseDetails").classList.remove("hidden");
}


document.addEventListener("DOMContentLoaded", loadCases);
