import { getAuthToken } from "./misc/api.js";

const form = document.querySelector("#loginForm");
form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const username = document.querySelector("#usernameInput").value;
    const password = document.querySelector("#passwordInput").value;

    try {
        const result = await getAuthToken(username, password);
        const messageContainer = document.querySelector("#message");

        if (!result) {
            console.error("Login failed! No access token received.");
            messageContainer.textContent =
                "Login failed. No access token received";
            return;
        }

        if (result.detail) {
            messageContainer.textContent = result.detail;
            return;
        }

        window.location.href = "/static/protected/chats.html";
    } catch (error) {
        console.error("Failed to log in. Error: ", error);
    }
});
