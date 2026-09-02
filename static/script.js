const messagesDiv = document.getElementById("messages");
const userInput = document.getElementById("user-input");
const sendButton = document.getElementById("send-button");

let isSending = false;
let stagedFile = null;         


function addMessage(text, sender) {
    const bubble = document.createElement("div");
    bubble.className = "message " + sender + "-message";

    if (typeof text === "string" && text.startsWith("IMAGE: ")) {
        const url = text.slice(7).trim();
        const img = document.createElement("img");
        img.alt = "image";
        img.style.maxWidth = "100%";
        img.style.borderRadius = "8px";
        // images load asynchronously and grow the scroll height after the
        // fact, so re-pin to bottom once each one finishes loading
        img.addEventListener("load", function () {
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        });
        img.src = url;
        bubble.appendChild(img);
    } else {
        bubble.textContent = text;
    }

    messagesDiv.appendChild(bubble);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}



function showThinking() {
    const bubble = document.createElement("div");
    bubble.className = "message agent-message thinking";
    bubble.id = "thinking-indicator";
    bubble.innerHTML = "<span></span><span></span><span></span>";
    messagesDiv.appendChild(bubble);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    return bubble;
}


function removeThinking() {
    const bubble = document.getElementById("thinking-indicator");
    if (bubble) {
        bubble.remove();
    }
}


// unified send: handles text-only AND image+text
async function sendMessage() {
    if (isSending) { return; }

    const text = userInput.value.trim();

    // check for either a message or a staged image to send anything
    if (text === "" && !stagedFile) { return; }

    isSending = true;
    userInput.disabled = true;
    sendButton.disabled = true;
    uploadButton.disabled = true;

    userInput.value = "";
    showThinking();

    try {
        if (stagedFile) {
            // image path
            const formData = new FormData();
            formData.append("image", stagedFile);

            const uploadResponse = await fetch("/upload", {
                method: "POST",
                body: formData,
            });
            if (!uploadResponse.ok) {
                throw new Error("Upload failed: " + uploadResponse.status);
            }
            const uploadData = await uploadResponse.json();
            const imageUrl = uploadData.url;

        
            removeThinking();
            clearStaged();
            const bubbleContent = text ? "IMAGE: " + imageUrl + "\n" + text : "IMAGE: " + imageUrl;
            addMessage("IMAGE: " + imageUrl, "user");  
            if (text) {
                addMessage(text, "user");                
            }
            showThinking();

            const analyzeResponse = await fetch("/analyze", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ image_url: imageUrl, question: text }),
            });
            if (!analyzeResponse.ok) {
                throw new Error("Analysis failed: " + analyzeResponse.status);
            }
            const analyzeData = await analyzeResponse.json();
            removeThinking();
            addMessage(analyzeData.reply, "agent");

        } else {
            // text-only path
            addMessage(text, "user");

            const response = await fetch("/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: text }),
            });
            if (!response.ok) {
                throw new Error("Server error: " + response.status);
            }
            const data = await response.json();
            removeThinking();
            addMessage(data.reply, "agent");
        }

    } catch (error) {
        removeThinking();
        addMessage("Something went wrong. Please try again.", "agent");
        console.error("sendMessage error:", error);
    } finally {
        isSending = false;
        userInput.disabled = false;
        sendButton.disabled = false;
        uploadButton.disabled = false;
        userInput.focus();
    }
}


async function loadHistory() {
    try {
        const response = await fetch("/history");
        const data = await response.json();
        for (const msg of data.messages) {
            addMessage(msg.text, msg.sender);
        }
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    } catch (error) {
        console.error("loadHistory error:", error);
    }
}


sendButton.addEventListener("click", sendMessage);

userInput.addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
        event.preventDefault();
        sendMessage();
    }
});


// image staging
const imageInput = document.getElementById("image-input");
const uploadButton = document.getElementById("upload-button");
const imagePreview = document.getElementById("image-preview");
const imagePreviewImg = document.getElementById("image-preview-img");
const imagePreviewName = document.getElementById("image-preview-name");


uploadButton.addEventListener("click", function () {
    imageInput.click();
});


function clearStaged() {
    stagedFile = null;
    imageInput.value = "";
    imagePreview.hidden = true;
    if (imagePreviewImg.src) {
        URL.revokeObjectURL(imagePreviewImg.src);
        imagePreviewImg.src = "";
    }
}


imageInput.addEventListener("change", function () {
    const file = imageInput.files[0];
    if (!file) { return; }
    stagedFile = file;

    // loady spinner
    const spinner = document.getElementById("image-preview-spinner");
    if (spinner) spinner.style.display = "block";  

    imagePreviewImg.onload = function () {
        if (spinner) spinner.style.display = "none"; 
    };
    imagePreviewImg.src = URL.createObjectURL(file);
    imagePreviewName.textContent = file.name;
    imagePreview.hidden = false;
    userInput.focus();
});
// theme toggle (lives inside the settings popover)
const themeToggle = document.getElementById("theme-toggle");

function setThemeSwitch(isDark) {
    themeToggle.setAttribute("aria-checked", isDark ? "true" : "false");
}

// apply saved theme on load (default: dark)
if (localStorage.getItem("theme") === "light") {
    document.body.classList.add("light");
    setThemeSwitch(false);
} else {
    setThemeSwitch(true);
}

themeToggle.addEventListener("click", function () {
    document.body.classList.toggle("light");
    const isLight = document.body.classList.contains("light");
    setThemeSwitch(!isLight);
    localStorage.setItem("theme", isLight ? "light" : "dark");
});

// settings popover
const settingsButton = document.getElementById("settings-button");
const settingsOverlay = document.getElementById("settings-overlay");
const settingsClose = document.getElementById("settings-close");
const modelInput = document.getElementById("model-input");
const compactThresholdInput = document.getElementById("compact-threshold-input");
const settingsStatus = document.getElementById("settings-status");

let settingsStatusTimer = null;

function showSettingsStatus(text) {
    settingsStatus.textContent = text;
    settingsStatus.classList.add("visible");
    clearTimeout(settingsStatusTimer);
    settingsStatusTimer = setTimeout(function () {
        settingsStatus.classList.remove("visible");
    }, 1500);
}

async function loadSettings() {
    try {
        const response = await fetch("/settings");
        const data = await response.json();
        modelInput.value = data.model || "";
        compactThresholdInput.value = data.compact_threshold || "";
    } catch (error) {
        console.error("loadSettings error:", error);
    }
}

async function saveSettings(payload) {
    try {
        const response = await fetch("/settings", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });
        const data = await response.json();
        if (!response.ok) {
            showSettingsStatus(data.error || "Could not save settings");
            return;
        }
        showSettingsStatus("Saved");
    } catch (error) {
        console.error("saveSettings error:", error);
        showSettingsStatus("Could not save settings");
    }
}

function openSettings() {
    settingsOverlay.hidden = false;
    loadSettings();
}

function closeSettings() {
    settingsOverlay.hidden = true;
}

settingsButton.addEventListener("click", openSettings);
settingsClose.addEventListener("click", closeSettings);

settingsOverlay.addEventListener("click", function (event) {
    if (event.target === settingsOverlay) {
        closeSettings();
    }
});

document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && !settingsOverlay.hidden) {
        closeSettings();
    }
});

modelInput.addEventListener("change", function () {
    const model = modelInput.value.trim();
    if (model) {
        saveSettings({ model: model });
    }
});

compactThresholdInput.addEventListener("change", function () {
    const value = parseInt(compactThresholdInput.value, 10);
    if (!isNaN(value) && value > 0) {
        saveSettings({ compact_threshold: value });
    }
});

loadHistory();
userInput.focus();

