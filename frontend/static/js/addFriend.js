import { getToken } from "./misc/auth.js";
import { addFriend } from "./misc/api.js";

const token = getToken();
if (!token) {
    console.error("Log in or register");
    window.location.href = "/";
}

const form = document.querySelector("#addFriendForm");
form.addEventListener("submit", async (event) => {
    event.preventDefault();

    try {
        const friendUsername = document.querySelector("#friendUsername").value;

        const result = await addFriend(token, friendUsername);
        if (!result) {
            console.error("Failed to send friend request");
            return;
        }

        console.log(result);
    } catch (error) {
        console.error("Add friend failed", error);
    }
});
