import { WS_BASE_URL } from "./config.js";
import {
    fetchCurrentUser,
    fetchMessageHistory,
    fetchFriends,
} from "./misc/api.js";
import { getToken } from "./misc/auth.js";

/* Add more error and status handling */

const token = getToken();
if (!token) {
    console.error("Log in or register");
    window.location.href = "/";
}

const currentUser = await fetchCurrentUser(token);
const currentUsername = currentUser.username;

const form = document.getElementById("messageForm");
form.hidden = true;

const chatMessages = document.getElementById("chatMessages");

let targetUser_ID;

let disappear = false;
function toggleDisappearingMessages() {
    disappear = !disappear;
    console.log(`Disappearing messages are now ${disappear}`);
}

const disappearingMessagesButton = document.getElementById(
    "disappearingMessagesButton",
);
disappearingMessagesButton.addEventListener(
    "click",
    toggleDisappearingMessages,
);

async function setTargetUserID(id) {
    targetUser_ID = id;
    form.hidden = false;
    chatMessages.innerHTML = "";

    const messages = await fetchMessageHistory(token, targetUser_ID);

    messages.forEach((message) => {
        if (message[4] === currentUsername) {
            message[4] = "You";
        }
        createMessageElement(message[4], message[2]);
    });

    console.log(`Target user ID set to: ${targetUser_ID}`);
}

function createMessageElement(user, message) {
    const p = document.createElement("p");
    const strong = document.createElement("strong");

    strong.textContent = `${user}: `;
    p.appendChild(strong);
    p.appendChild(document.createTextNode(message));

    chatMessages.appendChild(p);
}

async function showFriends() {
    const friendList = document.getElementById("friendList");

    const friends = await fetchFriends(token);
    if (!friends) {
        friendList.innerHTML = "<p>You have no friends ;(</p>";
        return;
    }

    friends.forEach((friend) => {
        const button = document.createElement("button");
        button.type = "button";
        button.textContent = friend[1];
        button.addEventListener("click", () => setTargetUserID(friend[0]));
        friendList.appendChild(button);
    });
}
showFriends();

const ws = new WebSocket(`${WS_BASE_URL}/ws?token=${token}`); // potem zmienić na dynamiczny adres serwera??????? potem sendowac token w ws.open()

ws.onopen = () => {
    console.log("Connected to websocket server");
};

ws.onmessage = (event) => {
    const message = JSON.parse(event.data);
    if (message.id != targetUser_ID) {
        return;
    }

    console.log("Received message:", message);
    if (message.error) {
        console.error(`Error from server: ${message.error}`);
        return;
    }

    createMessageElement(message.user, message.message);
};

ws.onerror = (error) => {
    console.error(`Websocket error: ${error}`);
};

ws.onclose = () => {
    console.log("Websocket closed");
};

form.addEventListener("submit", (event) => {
    event.preventDefault();

    const messageInput = document.getElementById("messageInput");
    ws.send(
        JSON.stringify({
            type: "text",
            targetUser_ID: targetUser_ID,
            content: messageInput.value,
            disappear: disappear,
        }),
    );

    createMessageElement("You", messageInput.value);

    messageInput.value = "";
});
