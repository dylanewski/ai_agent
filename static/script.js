const messagesDiv = document.getElementById("messages");
const userInput = document.getElementById("user-input");
const sendButton = document.getElementById("send-button");

let isSending = false;


function addMessage(text, sender) {
    const bubble = document.createElement("div");
    bubble.className = "message " + sender + "-message";

    if (typeof text === "string" && text.startsWith("IMAGE: ")) {
        const url = text.slice(7);
        const img = document.createElement("img");
        img.src = url;
        img.alt = "generated image";
        img.style.maxWidth = "100%";
        img.style.borderRadius = "8px";
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


async function sendMessage() {
    if (isSending) { return; }

    const text = userInput.value.trim();
    if (text === "") { return; }

    isSending = true;
    userInput.disabled = true;
    sendButton.disabled = true;

    addMessage(text, "user");
    userInput.value = "";

    showThinking();

    try {
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

    } catch (error) {
        removeThinking();
        addMessage("Something went wrong reaching the agent. Please try again.", "agent");
        console.error("sendMessage error:", error);
    } finally {
        isSending = false;
        userInput.disabled = false;
        sendButton.disabled = false;
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


const imageInput = document.getElementById("image-input");
const uploadButton = document.getElementById("upload-button");


uploadButton.addEventListener("click", function () {
    imageInput.click();
});


imageInput.addEventListener("change", async function () {
    const file = imageInput.files[0];
    if (!file) { return; }

    if (isSending) { return; }
    isSending = true;
    userInput.disabled = true;
    sendButton.disabled = true;
    uploadButton.disabled = true;


    const question = userInput.value.trim();
    userInput.value = "";

    showThinking();

    try {
        // 1. upload the image file to the server
        const formData = new FormData();
        formData.append("image", file);

        const uploadResponse = await fetch("/upload", {
            method: "POST",
            body: formData,       
        });

        if (!uploadResponse.ok) {
            throw new Error("Upload failed: " + uploadResponse.status);
        }

        const uploadData = await uploadResponse.json();
        const imageUrl = uploadData.url;

        // 2. show the uploaded image in the chat (as the user's message)
        removeThinking();
        addMessage("IMAGE: " + imageUrl, "user");
        showThinking();

        // 3. Analayze image with the question (if any) and get the agent's response
        const analyzeResponse = await fetch("/analyze", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ image_url: imageUrl, question: question }),
        });

        if (!analyzeResponse.ok) {
            throw new Error("Analysis failed: " + analyzeResponse.status);
        }

        const analyzeData = await analyzeResponse.json();
        removeThinking();
        addMessage(analyzeData.reply, "agent");

    } catch (error) {
        removeThinking();
        addMessage("Something went wrong with the image. Please try again.", "agent");
        console.error("image upload error:", error);
    } finally {
        isSending = false;
        userInput.disabled = false;
        sendButton.disabled = false;
        uploadButton.disabled = false;
        imageInput.value = "";       
        userInput.focus();
    }
});

loadHistory();
userInput.focus();

