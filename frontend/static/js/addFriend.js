import { addFriend } from "./misc/api.js";

const form = document.querySelector("#addFriendForm");
form.addEventListener("submit", async (event) => {
    event.preventDefault();

    try {
        const friendUsername = document.querySelector("#friendUsername").value;
        const messageContainer = document.querySelector("#message");

        const result = await addFriend(friendUsername);

        if (!result) {
            console.error("Failed to send friend request");
            messageContainer.textContent = "Failed to send friend request";
            return;
        }

        if (result.detail) {
            messageContainer.textContent = result.detail;
            return;
        }

        messageContainer.textContent = result.message;
    } catch (error) {
        console.error("Add friend failed", error);
        messageContainer.textContent = error;
    }
});
