// src/routes/boards/edit/[boardId]/+page.server.js
import { get_request } from '$lib/api';
import { error } from '@sveltejs/kit';

export async function load({ params, cookies }) {
    const boardId = params.boardId;
    const token = cookies.get('token'); // Get the auth token from cookies

    if (!token) {
        // If no token, redirect handled by auth store, but also throw error for load
        throw error(401, 'Unauthorized');
    }

    try {
        const board = await get_request(`/api/boards/${boardId}`, token);
        return {
            board: board
        };
    } catch (e) {
        console.error(`Error fetching board ${boardId}:`, e);
        // Throwing an error here will display an error page or can be caught in +page.svelte
        throw error(e.status || 500, e.message || `Failed to load board with ID ${boardId}.`);
    }
}