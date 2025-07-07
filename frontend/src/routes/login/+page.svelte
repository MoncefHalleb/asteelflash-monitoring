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

            const response = await fetch('/token', {
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

            let decoded;
            try {
                decoded = jwtDecode(accessToken);
                console.log('Frontend: Decoded Token Payload:', decoded); // Debugging
            } catch (decodeError) {
                console.error('Frontend: Error decoding JWT:', decodeError);
                throw new Error('Failed to decode authentication token.');
            }

            const user = decoded.sub; // 'sub' is the standard claim for the subject (username)
            const role = decoded.role; // Extract role from JWT payload

            console.log('Frontend: Extracted Username from Token:', user); // Debugging
            console.log('Frontend: Extracted Role from Token:', role); // Debugging

            authLogin(accessToken, user, role);

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
                <label for="username"><i class="ri-user-line"></i> Username</label>
                <input type="text" id="username" bind:value={username} required autocomplete="username" placeholder="Enter your username" />
            </div>

            <div class="form-group">
                <label for="password"><i class="ri-lock-line"></i> Password</label>
                <input type="password" id="password" bind:value={password} required autocomplete="current-password" placeholder="Enter your password" />
            </div>

            <button type="submit" disabled={isLoading}>
                {#if isLoading}
                    <div class="spinner-small"></div>
                    Logging In...
                {:else}
                    <i class="ri-login-circle-line"></i> Log In
                {/if}
            </button>
        </form>

        {#if errorMessage}
            <p class="error-message"><i class="ri-error-warning-fill"></i> {errorMessage}</p>
        {/if}

      
    </div>
</div>

<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    @import url('https://cdn.jsdelivr.net/npm/remixicon@4.3.0/fonts/remixicon.min.css');

    :root {
        --primary: #4db6ff; /* Refined sky blue for primary elements */
        --primary-dark: #1e90ff; /* Darker shade for hover states */
        --accent: #34c759; /* Vibrant green for secondary elements */
        --danger: #ff4d4f; /* Softer red for errors */
        --warn: #ffd700; /* Gold for warnings */
        --bg-dark: #12141c; /* Deep, modern background */
        --text-light: #f0f2f5; /* Bright off-white for readability */
        --text-dark-contrast: #1e1e2e; /* Dark navy for contrast */
        --card-bg: rgba(28, 30, 41, 0.85); /* Glassmorphism card background */
        --shadow: 0 8px 32px rgba(0, 0, 0, 0.35);
        --border: 1px solid rgba(77, 182, 255, 0.2);
        --glass-blur: 12px;
        --text-muted: #a0a5c0; /* Muted gray for placeholders */
    }

    :global(body) {
        margin: 0;
        font-family: 'Inter', sans-serif;
        background-color: var(--bg-dark);
        color: var(--text-light);
        line-height: 1.7;
        min-height: 00vh;
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
        background-position: center;
        background-size: 40%;
        background-repeat: no-repeat;
        opacity: 0.06;
        filter: grayscale(100%) brightness(40%);
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
        background: linear-gradient(135deg, rgba(18, 20, 28, 0.92) 0%, rgba(18, 20, 28, 0.98) 100%);
        z-index: -1;
        pointer-events: none;
    }

    .login-container {
        min-height: 100vh;
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 2rem;
    }

    .login-card {
        background-color: var(--card-bg);
        border-radius: 1.5rem;
        border: var(--border);
        box-shadow: var(--shadow);
        backdrop-filter: blur(var(--glass-blur));
        padding: 3.5rem;
        max-width: 550px;
        width: 100%;
        min-width: 320px;
        text-align: center;
        transition: transform 0.4s ease, box-shadow 0.4s ease, border 0.4s ease;
        display: flex;
        flex-direction: column;
        align-items: center;
        position: relative;
        overflow: hidden;
    }

    .login-card::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle at center, rgba(77, 182, 255, 0.15), transparent 70%);
        animation: glowRotate 8s linear infinite;
        pointer-events: none;
        opacity: 0.5;
    }

    @keyframes glowRotate {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    .login-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.5);
        border: 1.5px solid var(--primary);
    }

    .login-logo {
        width: 120px;
        height: 120px;
        object-fit: contain;
        margin-bottom: 2rem;
        border-radius: 1.2rem;
        box-shadow: 0 4px 16px rgba(77, 182, 255, 0.2);
        background: var(--card-background);
        padding: 1rem;
        transition: transform 0.4s ease, box-shadow 0.4s ease;
    }

    .login-logo:hover {
        transform: scale(1.1);
        box-shadow: 0 6px 20px rgba(77, 182, 255, 0.3);
    }

    .login-title {
        background: linear-gradient(135deg, var(--primary), var(--accent));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 3rem;
        font-size: 3rem;
        font-weight: 800;
        text-shadow: 0 0 16px rgba(77, 182, 255, 0.5);
        letter-spacing: -0.015em;
    }

    form {
        display: flex;
        flex-direction: column;
        gap: 2rem;
        width: 100%;
        max-width: 480px;
        margin: 0 auto;
    }

    .form-group {
        text-align: left;
        position: relative;
    }

    label {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        margin-bottom: 0.8rem;
        color: var(--text-light);
        font-weight: 600;
        font-size: 1.1rem;
    }

    label i {
        font-size: 1.3rem;
        color: var(--primary);
        transition: color 0.3s ease;
    }

    input[type="text"],
    input[type="password"] {
        width: 100%;
        padding: 1.2rem 1.5rem;
        border: 1px solid var(--border-color);
        border-radius: 1rem;
        background-color: rgba(255, 255, 255, 0.1);
        color: var(--text-light);
        font-size: 1.1rem;
        outline: none;
        transition: border-color 0.3s ease, box-shadow 0.3s ease, background-color 0.3s ease;
    }

    input[type="text"]::placeholder,
    input[type="password"]::placeholder {
        color: var(--text-muted);
        opacity: 0.9;
    }

    input[type="text"]:focus,
    input[type="password"]:focus {
        border-color: var(--primary);
        box-shadow: 0 0 0 4px rgba(77, 182, 255, 0.3);
        background-color: rgba(255, 255, 255, 0.15);
    }

    input[type="text"]:focus + label i,
    input[type="password"]:focus + label i {
        color: var(--accent);
    }

    button[type="submit"] {
        padding: 1.2rem 2rem;
        background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
        color: var(--text-dark-contrast);
        border: none;
        border-radius: 1rem;
        cursor: pointer announces that the cursor is a pointer, indicating a clickable element;
        font-weight: 700;
        font-size: 1.2rem;
        transition: all 0.4s ease;
        box-shadow: var(--shadow);
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.8rem;
        margin-top: 2rem;
        position: relative;
        overflow: hidden;
    }

    button[type="submit"]::after {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        background: rgba(255, 255, 255, 0.3);
        border-radius: 50%;
        transform: translate(-50%, -50%);
        transition: width 0.6s ease, height 0.6s ease;
    }

    button[type="submit"]:hover:not(:disabled)::after {
        width: 400px;
        height: 400px;
    }

    button[type="submit"]:hover:not(:disabled) {
        background: linear-gradient(135deg, var(--accent) 0%, var(--primary) 100%);
        transform: translateY(-4px);
        box-shadow: 0 10px 30px rgba(77, 182, 255, 0.4);
    }

    button[type="submit"]:disabled {
        background: rgba(77, 182, 255, 0.3);
        cursor: not-allowed;
        box-shadow: none;
        transform: none;
    }

    .spinner-small {
        border: 4px solid rgba(255, 255, 255, 0.3);
        border-top: 4px solid var(--primary);
        border-radius: 50%;
        width: 24px;
        height: 24px;
        animation: spin 0.8s linear infinite;
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    .error-message {
        color: var(--danger);
        margin-top: 2.2rem;
        font-size: 1.1rem;
        font-weight: 600;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.7rem;
        padding: 1rem;
        background-color: rgba(255, 77, 79, 0.15);
        border-radius: 0.75rem;
        border: 1px solid rgba(255, 77, 79, 0.3);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        animation: fadeIn 0.3s ease;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .error-message i {
        font-size: 1.4rem;
    }

    .register-link {
        margin-top: 3rem;
        color: var(--text-muted);
        font-size: 1.05rem;
    }

    .register-link a {
        color: var(--accent);
        text-decoration: none;
        font-weight: 700;
        transition: color 0.3s ease, text-shadow 0.3s ease;
    }

    .register-link a:hover {
        color: var(--primary);
        text-shadow: 0 0 8px rgba(77, 182, 255, 0.5);
    }

    @media (max-width: 700px) {
        .login-card {
            padding: 2.5rem 1.5rem;
            max-width: 95vw;
            min-width: unset;
        }

        .login-title {
            font-size: 2.5rem;
        }

        form {
            max-width: 100%;
        }

        button[type="submit"] {
            padding: 1rem 1.6rem;
            font-size: 1.1rem;
        }
    }

    @media (max-width: 400px) {
        .login-logo {
            width: 100px;
            height: 100px;
        }

        .login-title {
            font-size: 2.2rem;
        }
    }
</style>