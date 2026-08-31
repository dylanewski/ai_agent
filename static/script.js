// grab the elements we need from the page
const messagesDiv = document.getElementById("messages");
const userInput = document.getElementById("user-input");
const sendButton = document.getElementById("send-button");


// add one message bubble to the page
function addMessage(text, sender) {
    const bubble = document.createElement("div");
    bubble.className = "message " + sender + "-message";
    bubble.textContent = text;
    messagesDiv.appendChild(bubble);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}


// show the pulsing "thinking" dots while the agent works
function showThinking() {
    const bubble = document.createElement("div");
    bubble.className = "message agent-message thinking";
    bubble.id = "thinking-indicator";
    bubble.innerHTML = "<span></span><span></span><span></span>";
    messagesDiv.appendChild(bubble);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    return bubble;
}


// remove the thinking dots once we have a reply (or an error)
function removeThinking() {
    const bubble = document.getElementById("thinking-indicator");
    if (bubble) {
        bubble.remove();
    }
}


// send the user's message, show the reply (with thinking indicator + error handling)
async function sendMessage() {
    const text = userInput.value;
    if (text === "") { return; }

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
    }
}


// load and render the existing conversation when the page opens
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


// wire up the events
sendButton.addEventListener("click", sendMessage);

userInput.addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
        sendMessage();
    }
});

// run once on page load to show past conversation
loadHistory();