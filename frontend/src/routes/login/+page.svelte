<script>
    import { login as authLogin } from '../../stores/authStore.js'; // Alias to avoid name conflict
    import { jwtDecode } from 'jwt-decode'; // <--- IMPORTANT: You need this import here!
    import { goto } from '$app/navigation'; // For redirection

    let username = '';
    let password = '';
    let errorMessage = '';
    let isLoading = false; // State for loading indicator

    async function handleSubmit() {
        errorMessage = ''; // Clear previous errors
        isLoading = true; // Start loading

        try {
            const formData = new URLSearchParams();
            formData.append('username', username);
            formData.append('password', password);

            // Ensure this path matches your FastAPI endpoint.
            // If your FastAPI /token endpoint is at the root (as per your backend code), use '/token'.
            // If you changed it to /api/token in FastAPI, use '/api/token'.
            // Based on your provided backend, it's '/token'.
            const response = await fetch('/token', { // <--- Changed to '/token' (leading slash for root-relative)
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: formData.toString(),
            });

            console.log('Frontend: Login API Response Status:', response.status); // Debugging

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Login failed');
            }

            const data = await response.json();
            const accessToken = data.access_token;

            console.log('Frontend: Received Access Token:', accessToken); // Debugging

            // --- THIS IS THE CRITICAL PART: DECODING THE JWT ---
            let decoded;
            try {
                decoded = jwtDecode(accessToken);
                console.log('Frontend: Decoded Token Payload:', decoded); // Debugging: See the full payload
            } catch (decodeError) {
                console.error('Frontend: Error decoding JWT:', decodeError);
                throw new Error('Failed to decode authentication token.');
            }

            const user = decoded.sub; // 'sub' is the standard claim for the subject (username)
            const role = decoded.role; // <--- This extracts the 'role' claim from the JWT payload

            console.log('Frontend: Extracted Username from Token:', user); // Debugging
            console.log('Frontend: Extracted Role from Token:', role); // <--- CRUCIAL DEBUGGING POINT

            // Now, pass these extracted values to your authStore's login function
            // The authStore.js you provided will then store these.
            authLogin(accessToken, user, role);

            // Redirection is handled by authStore.login, so no need for goto() here.
            // goto('/dashboard');

        } catch (error) {
            console.error('Frontend: Login process error:', error); // Log the full error
            errorMessage = error.message || 'Login failed. Please check your credentials.';
        } finally {
            isLoading = false; // End loading
        }
    }
</script>

<div class="login-container">
    <div class="login-card">
        <img src="/images.png" alt="AsteelFlash Logo" class="login-logo" />
        <h1 class="login-title">ASTEELFLASH Login</h1>

        <form on:submit|preventDefault={handleSubmit}>
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" bind:value={username} required autocomplete="username" />
            </div>

            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" bind:value={password} required autocomplete="current-password" />
            </div>

            <button type="submit" disabled={isLoading}>
                {#if isLoading}
                    <div class="spinner-small"></div>
                    Logging In...
                {:else}
                    Log In
                {/if}
            </button>
        </form>

        {#if errorMessage}
            <p class="error-message"><i class="ri-error-warning-fill"></i> {errorMessage}</p>
        {/if}

        <p class="register-link">
            Don't have an account? <a href="/register">Register here</a>
        </p>
    </div>
</div>

<style>
    /* Your existing styles (ensure theme variables are defined globally or here) */
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

    .login-container {
        min-height: 100vh;
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 32px;
    }

    .login-card {
        background-color: var(--card-bg);
        border-radius: 1.25rem;
        border: var(--border);
        box-shadow: var(--shadow);
        backdrop-filter: blur(var(--glass-blur));
        -webkit-backdrop-filter: blur(var(--glass-blur-webkit));
        padding: 3rem 3.5rem;
        max-width: 600px;
        width: 100%;
        min-width: 350px;
        text-align: center;
        transition: box-shadow 0.3s ease, border 0.3s ease;
        display: flex;
        flex-direction: column;
        align-items: center;
    }

    .login-card:hover {
        box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.5);
        border: 1.5px solid var(--primary);
    }

    .login-logo {
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

    .login-title {
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
        max-width: 500px;
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
    input[type="password"] {
        width: 100%;
        padding: 1.1rem 1.4rem;
        border: 1px solid rgba(139, 233, 253, 0.25);
        border-radius: 0.85rem;
        background-color: rgba(40, 42, 54, 0.8);
        color: var(--text-light);
        font-size: 1.1rem;
        outline: none;
        transition: border-color 0.3s ease, box-shadow 0.3s ease, background-color 0.3s ease;
    }

    input[type="text"]:focus,
    input[type="password"]:focus {
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

    .error-message {
        color: var(--danger);
        margin-top: 2rem;
        font-size: 1.05rem;
        font-weight: 600;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.6rem;
        padding: 0.75rem;
        background-color: rgba(255, 85, 85, 0.1);
        border-radius: 0.5rem;
        border: 1px solid rgba(255, 85, 85, 0.3);
    }

    .error-message i {
        font-size: 1.3rem;
    }

    .register-link {
        margin-top: 2.5rem;
        color: var(--text-dark-contrast);
        font-size: 1rem;
    }

    .register-link a {
        color: var(--accent);
        text-decoration: none;
        font-weight: 700;
        transition: color 0.2s ease, text-decoration 0.2s ease;
    }

    .register-link a:hover {
        color: var(--primary);
        text-decoration: underline;
    }

    @media (max-width: 700px) {
        .login-card {
            padding: 2rem 1rem;
            max-width: 98vw;
            min-width: unset;
        }
        form {
            max-width: 100%;
        }
    }
</style>