import { API_BASE_URL } from "../config.js";

export async function apiFetch(endpoint, options = {}) {
    const headers = options.headers || {};

    if (
        options.body &&
        !(options.body instanceof URLSearchParams) &&
        !headers["Content-Type"]
    ) {
        headers["Content-Type"] = "application/json";
        options.body = JSON.stringify(options.body);
    }

    const res = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers,
    });

    const data = await res.json().catch(() => null);

    if (!res.ok) {
        console.error(`API error: ${res.status}`, data?.detail || data);
        return null;
    }

    return data;
}

export async function fetchCurrentUser() {
    return await apiFetch("/auth/me", {
        method: "GET",
        credentials: "include",
    });
}

export async function fetchMessageHistory(t_userID) {
    return await apiFetch(`/messages/${t_userID}`, {
        method: "GET",
        credentials: "include",
    });
}

export async function addFriend(friendUsername) {
    return await apiFetch("/addfriend", {
        method: "POST",
        body: { username: friendUsername },
        credentials: "include",
    });
}

export async function getAuthToken(username, password) {
    return await apiFetch("/auth/token", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({
            username: username,
            password: password,
        }),
    });
}

export async function registerUser(username, email, password, birthdate) {
    return await apiFetch("/auth/register", {
        method: "POST",
        body: { username, email, password, birthdate },
    });
}

export async function fetchFriends() {
    return await apiFetch("/friends", {
        method: "GET",
        credentials: "include",
    });
}
