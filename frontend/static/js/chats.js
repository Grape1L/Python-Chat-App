import { WS_BASE_URL } from "./config.js";
import {
    fetchCurrentUser,
    fetchMessageHistory,
    fetchFriends,
} from "./misc/api.js";
import {
    generatePrivateKey,
    calculateKey,
    encryptData,
    decryptData,
} from "./misc/encryption.js";

/* Add more error and status handling */

/* STATE */
const state = {
    currentUser: null,
    targetUser_ID: null,
    disappearingMessages: false,
};
/* STATE */

/* DOM */
const DOM = {
    messageForm: document.getElementById("messageForm"),
    chatMessages: document.getElementById("chatMessages"),
    disappearingMessages: document.getElementById("disappearingMessagesButton"),
    friendList: document.getElementById("friendList"),
    messageInput: document.getElementById("messageInput"),
    chatTitle: document.getElementById("chatTitle"),
};
/* DOM */

/* KEYS */
const keys = {
    privateKey: null,
    sharedKey: null,
};
/* KEYS */

/* INITS */
let ws;
function initWebsockets() {
    ws = new WebSocket(`${WS_BASE_URL}/ws`);

    ws.onopen = () => {
        console.log("Connected to websocket server");
    };

    ws.onmessage = async (event) => {
        const message = JSON.parse(event.data);
        console.log(message);

        if (message.id != state.targetUser_ID) {
            return;
        }

        console.log("Received message:", message);
        if (message.error) {
            console.error(`Error from server: ${message.error}`);
            return;
        }

        if (message.type === "key") {
            keys.sharedKey = calculateKey(
                keys.privateKey,
                BigInt(message.message),
            );
            console.log("keys.sharedKey: ", keys.sharedKey);

            if (message.firstSender === true) {
                let keyToSend = calculateKey(keys.privateKey);
                ws.send(
                    JSON.stringify({
                        type: "key",
                        targetUser_ID: state.targetUser_ID,
                        content: keyToSend.toString(),
                        disappear: true,
                        firstSender: false,
                    }),
                );
            }
            return;
        }

        const now = new Date();
        const utc = now.toISOString().slice(0, 19).replace("T", " ");

        const decryptedMessage = await decryptData(
            message.message,
            keys.sharedKey,
        );
        createMessageElement(message.user, decryptedMessage, utc);
    };

    ws.onerror = (error) => {
        console.error(`Websocket error: ${error}`);
    };

    ws.onclose = () => {
        console.log("Websocket closed");
    };
}

async function init() {
    DOM.messageForm.hidden = true;

    state.currentUser = await fetchCurrentUser();
    keys.privateKey = generatePrivateKey();

    await renderFriends();
    initWebsockets();
}

init();
/* INITS */

/* EVENTS */
DOM.disappearingMessages.addEventListener("click", toggleDisappearingMessages);
DOM.messageForm.addEventListener("submit", handleSendMessage);
/* EVENTS */

async function handleSendMessage(event) {
    event.preventDefault();

    const encryptedMessage = await encryptData(
        DOM.messageInput.value,
        keys.sharedKey,
    );
    console.log(encryptedMessage);

    ws.send(
        JSON.stringify({
            type: "text",
            targetUser_ID: state.targetUser_ID,
            content: encryptedMessage,
            disappear: state.disappearingMessages,
        }),
    );

    const now = new Date();
    const utc = now.toISOString().slice(0, 19).replace("T", " ");
    createMessageElement("You", DOM.messageInput.value, utc);

    DOM.messageInput.value = "";
}

function toggleDisappearingMessages() {
    state.disappearingMessages = !state.disappearingMessages;

    if (state.disappearingMessages === true) {
        DOM.disappearingMessages.textContent = "Disable disappearing messages";
    } else {
        DOM.disappearingMessages.textContent = "Enable disappearing messages";
    }
}

function createMessageElement(user, message, timestamp) {
    const p = document.createElement("p");
    p.appendChild(document.createTextNode(message));

    const timeSpan = document.createElement("span");
    timeSpan.textContent = ` [${timestamp}]`;
    timeSpan.style.fontSize = "0.8em";
    timeSpan.style.color = "#888";
    p.appendChild(timeSpan);

    if (user === "You") {
        p.style.textAlign = "right";
    }

    DOM.chatMessages.appendChild(p);
}

async function renderFriends() {
    const friends = await fetchFriends();

    if (friends.length === 0) {
        DOM.friendList.innerHTML = "<p>You have no friends ;(</p>";
        return;
    }

    friends.forEach((friend) => {
        const button = document.createElement("button");
        button.type = "button";
        button.textContent = friend[1];
        button.addEventListener("click", async () => {
            state.targetUser_ID = friend[0];

            console.log("keys.privateKey: ", keys.privateKey);
            let keyToSend = calculateKey(keys.privateKey);
            console.log("keyToSend: ", keyToSend);
            ws.send(
                JSON.stringify({
                    type: "key",
                    targetUser_ID: state.targetUser_ID,
                    content: keyToSend.toString(),
                    disappear: true,
                    firstSender: true,
                }),
            );

            DOM.messageForm.hidden = false;
            DOM.chatMessages.innerHTML = "";

            const messages = await fetchMessageHistory(state.targetUser_ID);

            messages.forEach(async (message) => {
                if (message[4] === state.currentUser.username) {
                    message[4] = "You";
                }

                const decryptedMessage = await decryptData(
                    message[2],
                    keys.sharedKey,
                );
                createMessageElement(message[4], decryptedMessage, message[3]);
            });

            DOM.chatTitle.textContent = friend[1];
        });
        DOM.friendList.appendChild(button);
    });
}
