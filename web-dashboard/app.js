const API_BASE = "http://localhost:8000/api/v1";

document.addEventListener("DOMContentLoaded", () => {
    fetchReviewQueue();
    document.getElementById("refreshBtn").addEventListener("click", fetchReviewQueue);
});

async function fetchReviewQueue() {
    const container = document.getElementById("cardsContainer");
    const countSpan = document.getElementById("queueCount");
    container.innerHTML = "<p>Loading pending reviews...</p>";

    try {
        const res = await fetch(`${API_BASE}/review-queue`);
        if (!res.ok) throw new Error("Failed to load review queue");

        const items = await res.json();
        countSpan.textContent = `${items.length} items pending review`;
        container.innerHTML = "";

        if (items.length === 0) {
            container.innerHTML = "<p>No items pending human review! All concepts verified with high confidence.</p>";
            return;
        }

        items.forEach(item => {
            const card = document.createElement("div");
            card.className = "card";

            const citationsHtml = (item.citations || []).map(c => `
                <li>
                    <strong><a href="${c.url}" target="_blank">${c.source_title || c.url}</a></strong>
                    <p style="margin: 4px 0 0; color: #4b5563;">"${c.supporting_quote || c.extracted_snippet || 'No quote'}"</p>
                </li>
            `).join("");

            card.innerHTML = `
                <div class="card-header">
                    <h2 style="margin: 0; font-size: 18px;">${item.concept_name}</h2>
                    <span class="badge">Confidence: ${(item.confidence_score * 100).toFixed(1)}%</span>
                </div>
                <div class="field">
                    <div class="field-label">Verified Definition (Editable)</div>
                    <textarea id="def_${item.entity_id}" rows="3">${item.verified_definition}</textarea>
                </div>
                <div class="field">
                    <div class="field-label">Grounding Citations (${(item.citations || []).length})</div>
                    <ul class="citations-list">
                        ${citationsHtml || "<li>No citations available</li>"}
                    </ul>
                </div>
                <button onclick="resolveItem('${item.entity_id}')">Approve & Save to Database</button>
            `;
            container.appendChild(card);
        });
    } catch (err) {
        console.error(err);
        container.innerHTML = `<p style="color: red;">Error connecting to API at ${API_BASE}. Ensure the FastAPI server is running.</p>`;
    }
}

async function resolveItem(entityId) {
    const updatedDef = document.getElementById(`def_${entityId}`).value;
    try {
        const res = await fetch(`${API_BASE}/review-queue/${entityId}/resolve?approved_definition=${encodeURIComponent(updatedDef)}`, {
            method: "POST"
        });
        if (res.ok) {
            fetchReviewQueue();
        } else {
            alert("Error resolving record.");
        }
    } catch (err) {
        alert("Failed to reach server.");
        console.error(err);
    }
}
