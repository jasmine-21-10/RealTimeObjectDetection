
const uploadForm = document.getElementById("uploadForm");

uploadForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const imageInput = document.getElementById("imageInput");
    const status = document.getElementById("uploadStatus");
    const button = document.getElementById("uploadButton");

    if (!imageInput.files.length) {
        status.textContent = "Please select an image.";
        return;
    }

    const formData = new FormData();
    formData.append("image", imageInput.files[0]);

    button.disabled = true;
    button.textContent = "Detecting...";
    status.textContent = "Processing image...";

    try {
        const response = await fetch("/upload", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Detection failed.");
        }

        document.getElementById("resultImage").src =
            data.result_image + "?t=" + Date.now();

        document.getElementById("uploadObjectCount").textContent =
            data.object_count;

        const list = document.getElementById("detectionList");
        list.replaceChildren();

        data.detections.forEach(function (item) {
            const li = document.createElement("li");
            li.textContent =
                `${item.class} — ${item.confidence}% confidence`;
            list.appendChild(li);
        });

        document.getElementById("uploadResult").hidden = false;
        status.textContent = "Detection completed successfully!";

    } catch (error) {
        status.textContent = error.message;
    } finally {
        button.disabled = false;
        button.textContent = "Detect Objects";
    }
});

async function loadHistory() {
    try {
        const response = await fetch("/api/history");
        const history = await response.json();

        const container = document.getElementById("historyList");

        if (!container) return;

        container.replaceChildren();

        if (history.length === 0) {
            container.textContent = "No detection history yet.";
            return;
        }

        history.forEach(function (item) {
            const card = document.createElement("div");
            card.className = "history-item";

            const title = document.createElement("h3");
            title.textContent = item.image;

            const time = document.createElement("p");
            time.textContent = "Time: " + item.time;

            const count = document.createElement("p");
            count.textContent = "Objects: " + item.object_count;

            const classes = document.createElement("p");
            classes.textContent = item.detections
                .map(d => `${d.class} (${d.confidence}%)`)
                .join(", ");

            const image = document.createElement("img");
            image.src = item.result_image;
            image.alt = "Detection result";
            image.width = 220;

            card.append(title, time, count, classes, image);
            container.appendChild(card);
        });
    } catch (error) {
        console.error("Could not load history:", error);
    }
}

loadHistory();
setInterval(loadHistory, 5000);
