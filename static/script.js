const messagesDiv = document.getElementById("messages");
const userInput = document.getElementById("user-input");
const sendButton = document.getElementById("send-button");

function addMessage(text, sender) {
    const bubble = document.createElement("div");
    bubble.className = "message " + sender + "-message";
    bubble.textContent = text;
    messagesDiv.appendChild(bubble);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

async function sendMessage() {
    const text = userInput.value;
    if (text === "") { return; }
    addMessage(text, "user");
    userInput.value = "";
    const response = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text }),
    });
    const data = await response.json();
    addMessage(data.reply, "agent");
}

sendButton.addEventListener("click", sendMessage);

userInput.addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
        sendMessage();
    }
});

async function loadHistory() {
    const response = await fetch("/history");
    const data = await response.json();
    for (const msg of data.messages) {
        addMessage(msg.text, msg.sender);
    }
}

loadHistory();