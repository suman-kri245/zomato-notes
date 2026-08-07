const API_URL = "http://127.0.0.1:8000";

async function loadNotes() {
    const container = document.getElementById("notesContainer");
    container.innerHTML = "Loading notes...";

    try {
        const response = await fetch(API_URL + "/notes");

        if (!response.ok) {
            throw new Error("HTTP " + response.status);
        }

        const notes = await response.json();

        container.innerHTML = "";

        if (notes.length === 0) {
            container.innerHTML = "<p>No notes found.</p>";
            return;
        }

        notes.forEach(function (note) {
            const div = document.createElement("div");

            div.innerHTML = `
                <h3>${note.title}</h3>
                <p>${note.content}</p>
                <p><strong>Tag:</strong> ${note.tag || "general"}</p>
                <p><strong>Owner ID:</strong> ${note.owner_id}</p>
                <p><strong>Note ID:</strong> ${note.id}</p>
                <hr>
            `;

            container.appendChild(div);
        });

    } catch (error) {
        console.error(error);
        container.innerHTML = `
            <p>Cannot load notes.</p>
            <p>${error.message}</p>
        `;
    }
}


async function createNote() {
    const title = document.getElementById("titleInput").value.trim();
    const content = document.getElementById("contentInput").value.trim();

    if (!title || !content) {
        alert("Please enter title and content.");
        return;
    }

    try {
        const response = await fetch(API_URL + "/notes", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                title: title,
                content: content,
                tag: "",
                owner_id: 1
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(
                errorData.detail || "HTTP " + response.status
            );
        }

        alert("Note created successfully!");

        document.getElementById("titleInput").value = "";
        document.getElementById("contentInput").value = "";

        loadNotes();

    } catch (error) {
        console.error(error);
        alert("Create failed: " + error.message);
    }
}


async function performSearch() {
    const value = document.getElementById("searchInput").value.trim();
    const type = document.getElementById("searchType").value;
    const results = document.getElementById("searchResults");

    if (!value) {
        results.innerHTML = "Please enter something.";
        return;
    }

    let url;

    if (type === "title") {
        url = API_URL + "/search/title?title=" +
            encodeURIComponent(value);

    } else if (type === "tag") {
        url = API_URL + "/search/tag?tag=" +
            encodeURIComponent(value);

    } else if (type === "tag-quick") {
        url = API_URL + "/search/tag-quick?tag=" +
            encodeURIComponent(value);

    } else if (type === "smart") {
        url = API_URL + "/notes/smart-search?q=" +
            encodeURIComponent(value);
    }

    try {
        const response = await fetch(url);

        if (!response.ok) {
            throw new Error("HTTP " + response.status);
        }

        const data = await response.json();

        results.innerHTML = "";

        if (!data || data.length === 0) {
            results.innerHTML = "No results found.";
            return;
        }

        data.forEach(function (item) {
            const note = type === "smart" ? item.note : item;

            const div = document.createElement("div");

            div.innerHTML = `
                <h3>${note.title}</h3>
                <p>${note.content}</p>
                <p>
                    <strong>Tag:</strong>
                    ${note.tag || "general"}
                </p>
                <p>
                    <strong>Owner ID:</strong>
                    ${note.owner_id}
                </p>
                ${
                    type === "smart"
                        ? `<p>
                            <strong>Similarity Score:</strong>
                            ${item.score.toFixed(4)}
                           </p>`
                        : ""
                }
                <hr>
            `;

            results.appendChild(div);
        });

    } catch (error) {
        console.error(error);
        results.innerHTML = "Search failed: " + error.message;
    }
}


window.onload = function () {
    loadNotes();
};
