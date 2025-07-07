<script>
    import { post } from '$lib/api';
    // No need to import goto here as redirection is handled by +page.js or authStore
    // import { goto } from '$app/navigation'; // <-- Can remove this line

    let username = '';
    let password = '';
    let role = 'user'; // Default role
    let message = '';
    let isError = false;
    let isLoading = false;

    async function handleSubmit() {
        message = '';
        isError = false;
        isLoading = true;
        try {
            const response = await post('/register-user', { username, password, role }, 'application/json');
            message = response.message || 'User added successfully!'; // Changed message
            isError = false;
            // Clear form fields on successful addition
            username = '';
            password = '';
            role = 'user'; // Reset role to default

            // No explicit redirect here, as user stays on "add user" page
            // setTimeout(() => goto('/login'), 1500); // Remove this line if staying on page
        } catch (error) {
            console.error('Add user error:', error); // Changed error log
            message = error.message || 'Failed to add user. Please try again.'; // Changed message
            isError = true;
        } finally {
            isLoading = false;
        }
    }
</script>

<div class="register-container"> <div class="register-card"> <img src="/images.png" alt="AsteelFlash Logo" class="register-logo" /> <h1 class="register-title">Add New User</h1> <form on:submit|preventDefault={handleSubmit}>
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" bind:value={username} required autocomplete="off" /> </div>

            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" bind:value={password} required autocomplete="new-password" />
            </div>

            <div class="form-group">
                <label for="role">Role</label>
                <select id="role" bind:value={role}>
                    <option value="user">User</option>
                    <option value="admin">Admin</option>
                </select>
            </div>

            <button type="submit" disabled={isLoading}>
                {#if isLoading}
                    <div class="spinner-small"></div>
                    Adding User...
                {:else}
                    Add User
                {/if}
            </button>
        </form>

        {#if message}
            <p class={isError ? 'error-message' : 'success-message'}>
                {#if isError}
                    <i class="ri-error-warning-fill"></i>
                {:else}
                    <i class="ri-check-circle-fill"></i>
                {/if}
                {message}
            </p>
        {/if}

        </div>
</div>

<style>
    /*
    * IMPORTANT:
    * The :root variables, global font imports, and global body styles
    * should ideally be defined ONCE in src/routes/+layout.svelte or src/app.css.
    * I'm including them here for self-containment in this example,
    * but for a real SvelteKit app, avoid duplication.
    */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    @import url('https://cdn.jsdelivr.net/npm/remixicon@4.2.0/fonts/remixicon.min.css');

    :root {
        --primary: #8be9fd;
        --primary-dark: #62d8f7;
        --accent: #50fa7b;
        --success: #2e7d32;
        --danger: #ff5555;
        --warn: #f1fa8c;
        --bg-dark: #282a36;
        --text-light: #f8f8f2;
        --text-dark-contrast: #cccccc;
        --card-bg: rgba(68, 71, 90, 0.6);
        --glass-blur: 16px;
        --shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4);
        --border: 1px solid rgba(139, 233, 253, 0.1);
        --glass-blur-webkit: 16px;
    }

    :global(body) {
        margin: 0;
        font-family: 'Inter', sans-serif;
        background-color: var(--bg-dark);
        color: var(--text-light);
        line-height: 1.6;
        position: relative;
        min-height: 100vh;
        overflow-x: hidden;
    }

    :global(body)::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: url('/images.png');
        background-position: center center;
        background-size: 50%;
        background-repeat: no-repeat;
        opacity: 0.04;
        filter: grayscale(100%) brightness(50%);
        z-index: -2;
        pointer-events: none;
    }

    :global(body)::after {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(135deg, rgba(40, 42, 54, 0.9) 0%, rgba(40, 42, 54, 0.95) 100%);
        z-index: -1;
        pointer-events: none;
    }

    /* Renamed container/card classes for semantic clarity for "Add User" */
    .register-container { /* Kept original class name for less refactoring, but conceptually it's "add-user-container" */
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
        padding: 20px;
        box-sizing: border-box;
        z-index: 0;
        position: relative;
    }

    .register-card { /* Kept original class name for less refactoring, but conceptually it's "add-user-card" */
        background-color: var(--card-bg);
        border-radius: 1.25rem;
        border: var(--border);
        box-shadow: var(--shadow);
        backdrop-filter: blur(var(--glass-blur));
        -webkit-backdrop-filter: blur(var(--glass-blur-webkit));
        padding: 3rem;
        max-width: 450px;
        width: 100%;
        text-align: center;
        transition: box-shadow 0.3s ease, border 0.3s ease;
        display: flex;
        flex-direction: column;
        align-items: center;
    }

    .register-card:hover {
        box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.5);
        border: 1.5px solid var(--primary);
    }

    .register-logo {
        width: 100px;
        height: 100px;
        object-fit: contain;
        margin-bottom: 1.5rem;
        border-radius: 1rem;
        box-shadow: 0 2px 12px rgba(139,233,253,0.12);
        background: #23243a;
        padding: 0.75rem;
        display: block;
    }

    .register-title {
        color: var(--primary);
        margin-bottom: 2.5rem;
        font-size: 2.8rem;
        font-weight: 800;
        text-shadow: 0 0 15px rgba(139, 233, 253, 0.5);
        letter-spacing: 0.05em;
    }

    form {
        display: flex;
        flex-direction: column;
        gap: 1.75rem;
        width: 100%;
        max-width: 380px;
        margin: 0 auto;
    }

    .form-group {
        text-align: left;
    }

    label {
        display: block;
        margin-bottom: 0.75rem;
        color: var(--text-dark-contrast);
        font-weight: 600;
        font-size: 1.05rem;
    }

    input[type="text"],
    input[type="password"],
    select {
        width: 100%;
        padding: 1.1rem 1.4rem;
        border: 1px solid rgba(139, 233, 253, 0.25);
        border-radius: 0.85rem;
        background-color: rgba(40, 42, 54, 0.8);
        color: var(--text-light);
        font-size: 1.1rem;
        outline: none;
        transition: border-color 0.3s ease, box-shadow 0.3s ease, background-color 0.3s ease;
        -webkit-appearance: none;
        -moz-appearance: none;
        appearance: none;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' width='24' height='24'%3E%3Cpath fill='%23ccc' d='M7 10l5 5 5-5z'/%3E%3C/svg%3E");
        background-repeat: no-repeat;
        background-position: right 1rem center;
        background-size: 1.2em;
    }

    input[type="text"]:focus,
    input[type="password"]:focus,
    select:focus {
        border-color: var(--primary);
        box-shadow: 0 0 0 4px rgba(139, 233, 253, 0.4);
        background-color: rgba(40, 42, 54, 0.9);
    }

    button[type="submit"] {
        padding: 1.1rem 1.8rem;
        background: linear-gradient(90deg, var(--primary) 0%, var(--accent) 100%);
        color: var(--bg-dark);
        border: none;
        border-radius: 0.85rem;
        cursor: pointer;
        font-weight: 700;
        font-size: 1.2rem;
        transition: all 0.3s ease;
        box-shadow: 0 6px 20px rgba(80, 250, 123, 0.3);
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.75rem;
        margin-top: 1.75rem;
    }

    button[type="submit"]:hover:not(:disabled) {
        background: linear-gradient(90deg, var(--accent) 0%, var(--primary) 100%);
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(80, 250, 123, 0.4);
    }

    button[type="submit"]:disabled {
        background: rgba(139, 233, 253, 0.3);
        cursor: not-allowed;
        box-shadow: none;
        transform: none;
    }

    .spinner-small {
        border: 3px solid rgba(255, 255, 255, 0.3);
        border-top: 3px solid var(--text-light);
        border-radius: 50%;
        width: 20px;
        height: 20px;
        animation: spin 1s linear infinite;
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    .success-message,
    .error-message {
        margin-top: 2rem;
        font-size: 1.05rem;
        font-weight: 600;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.6rem;
        padding: 0.75rem;
        border-radius: 0.5rem;
    }

    .success-message {
        color: var(--accent);
        background-color: rgba(80, 250, 123, 0.1);
        border: 1px solid rgba(80, 250, 123, 0.3);
    }

    .error-message {
        color: var(--danger);
        background-color: rgba(255, 85, 85, 0.1);
        border: 1px solid rgba(255, 85, 85, 0.3);
    }

    .success-message i,
    .error-message i {
        font-size: 1.3rem;
    }

    /* Removed login-link as this is an admin-only page */
    /* .login-link {
        margin-top: 2.5rem;
        color: var(--text-dark-contrast);
        font-size: 1rem;
    }

    .login-link a {
        color: var(--accent);
        text-decoration: none;
        font-weight: 700;
        transition: color 0.2s ease, text-decoration 0.2s ease;
    }

    .login-link a:hover {
        color: var(--primary);
        text-decoration: underline;
    } */
</style>