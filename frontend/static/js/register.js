import { registerUser } from "./misc/api";
import { saveToken } from "./misc/auth";

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

        saveToken(result.access_token);

        window.location.href = "/static/protected/chats.html";
    } catch (error) {
        console.error("Failed to register. Error: ", error);
    }
});
