
// =====================================================
// API URL
// =====================================================

const API_URL = "http://127.0.0.1:8000";


// =====================================================
// LOAD NOTES
// =====================================================

async function loadNotes() {

    const container =
        document.getElementById("notesContainer");

    container.innerHTML =
        "<p>Loading...</p>";

    try {

        const response =
            await fetch(
                API_URL + "/notes"
            );

        if (!response.ok) {

            throw new Error(
                "HTTP " + response.status
            );

        }

        const notes =
            await response.json();

        console.log(
            "NOTES:",
            notes
        );

        container.innerHTML = "";

        if (
            !notes ||
            notes.length === 0
        ) {

            container.innerHTML =
                "<p>No notes found.</p>";

            return;
        }

        notes.forEach(function(note) {

            const card =
                document.createElement("div");

            card.className = "note";

            card.innerHTML = `

                <h3>
                    ${note.title || "No title"}
                </h3>

                <p>
                    ${note.content || "No content"}
                </p>

                <p>
                    <strong>Tag:</strong>
                    ${note.tag || "general"}
                </p>

                <p>
                    <strong>Owner ID:</strong>
                    ${note.owner_id || ""}
                </p>

                <p>
                    <strong>Note ID:</strong>
                    ${note.id || ""}
                </p>

                <p>
                    <strong>Created:</strong>
                    ${note.created_at || ""}
                </p>

            `;

            container.appendChild(card);

        });

    }
    catch (error) {

        console.error(
            "LOAD ERROR:",
            error
        );

        container.innerHTML = `

            <p class="error">
                <strong>
                    Error loading notes:
                </strong>

                ${error.message}
            </p>

        `;
    }
}


// =====================================================
// CREATE NOTE
// =====================================================

async function createNote() {

    const title =
        document
            .getElementById("titleInput")
            .value
            .trim();

    const content =
        document
            .getElementById("contentInput")
            .value
            .trim();

    if (
        !title ||
        !content
    ) {

        alert(
            "Please enter title and content."
        );

        return;
    }

    try {

        const response =
            await fetch(
                API_URL + "/notes",
                {

                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        title: title,

                        content: content,

                        tag: "",

                        owner_id: 1

                    })

                }
            );

        if (!response.ok) {

            throw new Error(
                "HTTP " + response.status
            );

        }

        const data =
            await response.json();

        console.log(
            "CREATED NOTE:",
            data
        );

        alert(
            "Note created successfully!"
        );

        document
            .getElementById("titleInput")
            .value = "";

        document
            .getElementById("contentInput")
            .value = "";

        await loadNotes();

    }
    catch (error) {

        console.error(
            "CREATE ERROR:",
            error
        );

        alert(
            "Create failed: " +
            error.message
        );
    }
}


// =====================================================
// SEARCH NOTES
// =====================================================

async function performSearch() {

    const value =
        document
            .getElementById("searchInput")
            .value
            .trim();

    const type =
        document
            .getElementById("searchType")
            .value;

    const results =
        document
            .getElementById("searchResults");

    if (!value) {

        results.innerHTML =
            "<p>Please enter something to search.</p>";

        return;
    }


    // =================================================
    // CREATE SEARCH URL
    // =================================================

    let url = "";


    // -------------------------------------------------
    // TITLE SEARCH
    // -------------------------------------------------

    if (type === "title") {

        url =
            API_URL +
            "/search/title?title=" +
            encodeURIComponent(value);
    }


    // -------------------------------------------------
    // TAG SEARCH
    // -------------------------------------------------

    else if (type === "tag") {

        url =
            API_URL +
            "/search/tag?tag=" +
            encodeURIComponent(value);
    }


    // -------------------------------------------------
    // TAG QUICK SEARCH
    // -------------------------------------------------

    else if (type === "tag-quick") {

        url =
            API_URL +
            "/search/tag-quick?tag=" +
            encodeURIComponent(value);
    }


    // -------------------------------------------------
    // SMART SEARCH
    // -------------------------------------------------

    else if (type === "smart") {

        url =
            API_URL +
            "/notes/smart-search?q=" +
            encodeURIComponent(value);
    }


    console.log(
        "SEARCH TYPE:",
        type
    );

    console.log(
        "SEARCH URL:",
        url
    );


    results.innerHTML =
        "<p>Searching...</p>";


    try {

        const response =
            await fetch(url);


        if (!response.ok) {

            throw new Error(
                "HTTP " +
                response.status
            );
        }


        const data =
            await response.json();


        console.log(
            "SEARCH RESULT:",
            data
        );


        results.innerHTML = "";


        // =================================================
        // NORMALIZE RESPONSE
        // =================================================

        let items = [];


        if (Array.isArray(data)) {

            items = data;

        }
        else if (data) {

            items = [data];

        }


        // =================================================
        // NO RESULTS
        // =================================================

        if (
            items.length === 0
        ) {

            results.innerHTML =
                "<p>No results found.</p>";

            return;
        }


        // =================================================
        // DISPLAY RESULTS
        // =================================================

        items.forEach(function(item) {

            const note = item;


            const card =
                document.createElement("div");


            card.className =
                "note";


            card.innerHTML = `

                <h3>
                    ${note.title || "No title"}
                </h3>

                <p>
                    ${note.content || "No content"}
                </p>

                <p>
                    <strong>Tag:</strong>
                    ${note.tag || "general"}
                </p>

                <p>
                    <strong>Owner ID:</strong>
                    ${note.owner_id || ""}
                </p>

                <p>
                    <strong>Note ID:</strong>
                    ${note.id || ""}
                </p>

                <p>
                    <strong>Created:</strong>
                    ${note.created_at || ""}
                </p>

            `;


            // =================================================
            // SMART SEARCH RELEVANCE SCORE
            // =================================================

            if (
                type === "smart" &&
                note.similarity_score !== undefined
            ) {

                const score =
                    document.createElement("p");


                score.className =
                    "score";


                score.innerHTML = `

                    <strong>
                        Relevance Score:
                    </strong>

                    ${Number(
                        note.similarity_score
                    ).toFixed(3)}

                `;


                card.appendChild(score);
            }


            results.appendChild(card);

        });

    }
    catch (error) {

        console.error(
            "SEARCH ERROR:",
            error
        );


        results.innerHTML = `

            <p class="error">

                <strong>
                    Search failed:
                </strong>

                ${error.message}

            </p>

        `;
    }
}

