import { API_BASE_URL } from "../config.js";

/* Do 1 fetch instead of all of these */

export async function fetchCurrentUser(token) {
    const res = await fetch(`${API_BASE_URL}/auth/me`, {
        method: "GET",
        headers: {
            Authorization: `Bearer ${token}`,
        },
    });
    if (!res.ok) {
        console.error("You need to log in or register");
        window.location.href = "/";
        return;
    }

    const userData = await res.json();
    return userData;
}

export async function fetchMessageHistory(token, t_userID) {
    const res = await fetch(`${API_BASE_URL}/messages/${t_userID}`, {
        method: "GET",
        headers: {
            Authorization: `Bearer ${token}`,
        },
    });

    const messagesData = await res.json();
    return messagesData;
}

export async function addFriend(token, friendUsername) {
    const res = await fetch(`${API_BASE_URL}/addfriend`, {
        method: "POST",
        headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ username: friendUsername }),
    });
    const result = await res.json();
    if (!res.ok) {
        console.error("Failed to add friend. ", result.detail);
        return result;
    }

    return result;
}

export async function getAuthToken(username, password) {
    const res = await fetch(`${API_BASE_URL}/auth/token`, {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
        },
        body: new URLSearchParams({
            username: username,
            password: password,
        }),
    });

    const result = await res.json();

    if (!res.ok) {
        console.log("Login failed! ", result);
        return;
    }

    if (!result.access_token) {
        console.error("Login failed! No access token received.");
        return;
    }

    return result;
}

export async function registerUser(username, email, password, birthdate) {
    const res = await fetch(`${API_BASE_URL}/auth/register`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, email, password, birthdate }),
    });

    const result = await res.json();

    if (!res.ok) {
        console.log("Registration failed! ", result);
        return;
    }

    if (!result.access_token) {
        console.error("Registration failed! No access token received.");
        return;
    }

    return result;
}

export async function fetchFriends(token) {
    const res = await fetch(`${API_BASE_URL}/friends`, {
        method: "GET",
        headers: {
            Authorization: `Bearer ${token}`,
        },
    });

    const result = await res.json();
    if (!res.ok) {
        console.error("Failed to fetch friends. ", result.detail);
        return;
    }

    return result;
}
