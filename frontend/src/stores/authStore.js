// src/stores/authStore.js
import { writable } from 'svelte/store';
import { goto } from '$app/navigation'; // For navigation

const ACCESS_TOKEN_KEY = 'accessToken';
const USERNAME_KEY = 'username';
const USER_ROLE_KEY = 'userRole';

// Initialize the store with values from localStorage if they exist
const initialAccessToken = typeof window !== 'undefined' ? localStorage.getItem(ACCESS_TOKEN_KEY) : null;
const initialUsername = typeof window !== 'undefined' ? localStorage.getItem(USERNAME_KEY) : null;
const initialUserRole = typeof window !== 'undefined' ? localStorage.getItem(USER_ROLE_KEY) : null;

export const auth = writable({
    isAuthenticated: !!initialAccessToken, // true if token exists
    accessToken: initialAccessToken,
    username: initialUsername,
    userRole: initialUserRole
});

export function login(token, username, role) {
    if (typeof window !== 'undefined') {
        localStorage.setItem(ACCESS_TOKEN_KEY, token);
        localStorage.setItem(USERNAME_KEY, username);
        localStorage.setItem(USER_ROLE_KEY, role);
    }
    auth.set({
        isAuthenticated: true,
        accessToken: token,
        username: username,
        userRole: role
    });
    goto('/dashboard'); // Redirect to dashboard after successful login
}

export function logout() {
    if (typeof window !== 'undefined') {
        localStorage.removeItem(ACCESS_TOKEN_KEY);
        localStorage.removeItem(USERNAME_KEY);
        localStorage.removeItem(USER_ROLE_KEY);
    }
    auth.set({
        isAuthenticated: false,
        accessToken: null,
        username: null,
        userRole: null
    });
    goto('/login'); // Redirect to login page after logout
}