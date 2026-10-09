document.addEventListener('DOMContentLoaded', async () => {
    // Auto-fill selected text from active tab if available
    try {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        chrome.scripting.executeScript({
            target: { tabId: tab.id },
            func: () => window.getSelection().toString()
        }, (results) => {
            if (results && results[0] && results[0].result) {
                document.getElementById('definition').value = results[0].result.trim();
            }
        });
    } catch (e) {
        console.log("Could not auto-fetch selection:", e);
    }

    document.getElementById('submitBtn').addEventListener('click', async () => {
        const payload = {
            entity_id: "ext_" + Date.now(),
            subject: document.getElementById('subject').value || "General",
            grade_level: document.getElementById('grade_level').value || "General",
            concept_name: document.getElementById('concept_name').value || "Untitled Concept",
            unverified_definition: document.getElementById('definition').value || ""
        };

        const statusDiv = document.getElementById('status');
        statusDiv.textContent = "Sending to verification queue...";

        try {
            const response = await fetch('http://localhost:8000/api/v1/verify-entity', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (response.ok) {
                statusDiv.textContent = "Successfully scheduled for verification!";
            } else {
                statusDiv.textContent = "Error: Backend rejected request.";
            }
        } catch (err) {
            statusDiv.textContent = "Connection failed. Is backend running?";
            console.error(err);
        }
    });
});
