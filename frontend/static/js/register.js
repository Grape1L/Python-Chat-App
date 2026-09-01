import { registerUser } from "./misc/api.js";

const form = document.querySelector("#registerForm");
form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const username = document.querySelector("#username").value;
    const email = document.querySelector("#email").value;
    const password = document.querySelector("#password").value;
    const birthdate = document.querySelector("#birthdate").value;

    try {
        const result = await registerUser(username, email, password, birthdate);
        console.log(result);
        const messageContainer = document.querySelector("#message");

        if (!result) {
            console.error("Registration failed");
            messageContainer.textContent = "Registration failed";
            return;
        }

        if (result.detail) {
            messageContainer.textContent = result.detail;
            return;
        }

        window.location.href = "/static/protected/chats.html";
    } catch (error) {
        console.error("Failed to register. Error: ", error);
    }
});
