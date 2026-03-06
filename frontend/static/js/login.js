import { saveToken } from "./misc/auth.js";
import { getAuthToken } from "./misc/api.js";

const form = document.querySelector("#loginForm");
form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const username = document.querySelector("#usernameInput").value;
    const password = document.querySelector("#passwordInput").value;

    try {
        const result = await getAuthToken(username, password);
        console.log(result);

        if (!result || !result.access_token) {
            console.error("Login failed! No access token received.");
            return;
        }

        saveToken(result.access_token);

        window.location.href = "/static/protected/chats.html";
    } catch (error) {
        console.error("Failed to log in. Error: ", error);
    }
});
