// src/lib/api.js
import { auth } from '../stores/authStore';
import { get } from 'svelte/store'; // To read from the store

const BASE_URL = "http://127.0.0.1:8000"; // Your FastAPI backend URL

async function api(method, endpoint, data = null, contentType = 'application/json') {
    const { accessToken } = get(auth); // Get the current access token from the store
    const headers = {};

    if (accessToken) {
        headers['Authorization'] = `Bearer ${accessToken}`;
    }

    let body = null;
    if (data) {
        if (contentType === 'application/json') {
            headers['Content-Type'] = contentType;
            body = JSON.stringify(data);
        } else if (contentType === 'application/x-www-form-urlencoded') {
            headers['Content-Type'] = contentType;
            // For x-www-form-urlencoded, data should be an object that can be converted
            body = new URLSearchParams(data).toString();
        }
    }

    const response = await fetch(`${BASE_URL}${endpoint}`, {
        method: method,
        headers: headers,
        body: body
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        // Handle specific error codes like 401 (Unauthorized)
        if (response.status === 401 && endpoint !== '/token') {
             // If token is invalid/expired, log out the user
            auth.update(state => ({ ...state, isAuthenticated: false, accessToken: null, username: null, userRole: null }));
            // Optionally, redirect to login: goto('/login');
            throw new Error(`Unauthorized: ${errorData.detail}`);
        } else if (response.status === 403) {
            throw new Error(`Forbidden: ${errorData.detail}`);
        }
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    // Attempt to parse JSON, but don't fail if the response is empty (e.g., 204 No Content)
    const text = await response.text();
    return text ? JSON.parse(text) : null;
}

export const post = (endpoint, data, contentType) => api('POST', endpoint, data, contentType);
export const put = (endpoint, data, contentType) => api('PUT', endpoint, data, contentType);
export const get_request = (endpoint) => api('GET', endpoint); // Renamed to avoid conflict with Svelte's get