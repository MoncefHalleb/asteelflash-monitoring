// src/routes/register/+page.js
import { redirect } from '@sveltejs/kit';
import { auth } from '../../stores/authStore.js'; // Adjust path if necessary

export async function load() {
    let isAuthenticated;
    let userRole;

    // We need to get the current state of the store
    // This is how you access a Svelte store's value outside a Svelte component.
    auth.subscribe(value => {
        isAuthenticated = value.isAuthenticated;
        userRole = value.userRole;
    })(); // Call the subscription function immediately to get current value

    if (!isAuthenticated) {
        throw redirect(302, '/login'); // Not logged in, redirect to login
    }

    if (userRole !== 'admin') {
        throw redirect(302, '/dashboard'); // Logged in but not admin, redirect to dashboard or an unauthorized page
    }

    // If authenticated and admin, allow access to the page
    return {}; // Return an empty object if no props are needed for the page
}