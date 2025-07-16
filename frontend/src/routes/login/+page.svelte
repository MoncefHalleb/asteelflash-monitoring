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
    --accent: #34c759; /* Vibrant green for secondary elements, aligned with table styles */
    --accent-dark: #28a745; /* Darker accent for hover states */
    --danger: #ff4d4f; /* Softer red for errors */
    --warn: #ffd700; /* Gold for warnings */
    --bg-dark: #12141c; /* Deep, modern background */
    --text-light: #f0f2f5; /* Bright off-white for readability */
    --text-dark-contrast: #1e1e2e; /* Dark navy for contrast */
    --card-bg: rgba(28, 30, 41, 0.9); /* Slightly more opaque glassmorphism */
    --shadow-soft: 0 6px 24px rgba(0, 0, 0, 0.3); /* Softer shadow, aligned with tables */
    --shadow-glow: 0 0 12px 2px rgba(52, 199, 89, 0.3); /* Accent-based glow, matching table styles */
    --border: 1px solid rgba(77, 182, 255, 0.25); /* Slightly stronger border */
    --glass-blur: 14px; /* Enhanced blur for glassmorphism */
    --text-muted: #a0a5c0; /* Muted gray for placeholders */
    --gradient-primary: linear-gradient(135deg, var(--primary) 0%, #1a874b 100%); /* Aligned with table gradients */
    --gradient-accent: linear-gradient(135deg, var(--accent) 0%, #21a66a 100%); /* Aligned with table gradients */
    --gradient-accent-hover: linear-gradient(135deg, var(--accent-dark) 0%, #188050 100%); /* Aligned with table hover gradients */
}

:global(body) {
    margin: 0;
    font-family: 'Inter', sans-serif;
    background-color: var(--bg-dark);
    color: var(--text-light);
    line-height: 1.7;
    min-height: 100vh;
    overflow-x: hidden;
    background-image: url('/images1.png');
    background-repeat: repeat-x;
    background-size: cover;
    animation: move-background 40s linear infinite; /* Smoother, faster animation */
    will-change: background-position;
}

@keyframes move-background {
    0% { background-position: 0% 0%; }
    100% { background-position: 100% 0%; }
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
    background-size: 35%; /* Slightly smaller for subtlety */
    background-repeat: no-repeat;
    opacity: 0.08; /* Slightly more visible */
    filter: grayscale(100%) brightness(50%); /* Adjusted for better contrast */
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
    background: linear-gradient(135deg, rgba(18, 20, 28, 0.9) 0%, rgba(18, 20, 28, 0.95) 100%); /* Slightly lighter gradient */
    z-index: -1;
    pointer-events: none;
}

.login-container {
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 2.5rem; /* Slightly more padding */
}

.login-card {
    background-color: var(--card-bg);
    border-radius: 1.8rem; /* More rounded corners */
    border: var(--border);
    box-shadow: var(--shadow-soft);
    backdrop-filter: blur(var(--glass-blur));
    padding: 4rem 3rem; /* More spacious padding */
    max-width: 600px; /* Slightly wider for better form layout */
    width: 100%;
    min-width: 340px; /* Adjusted for smaller screens */
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
    background: radial-gradient(circle at center, rgba(52, 199, 89, 0.2), transparent 70%); /* Aligned with accent color */
    animation: glowRotate 10s linear infinite; /* Smoother rotation */
    pointer-events: none;
    opacity: 0.4; /* Slightly less intense */
}

@keyframes glowRotate {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.login-card:hover {
    transform: translateY(-10px) scale(1.01); /* More pronounced lift */
    box-shadow: var(--shadow-glow), 0 14px 48px rgba(0, 0, 0, 0.4); /* Stronger shadow */
    border: 1.5px solid var(--accent); /* Accent border on hover */
}

.login-logo {
    width: 140px; /* Slightly larger for prominence */
    height: 140px;
    object-fit: contain;
    margin-bottom: 2.5rem;
    border-radius: 1.5rem; /* More rounded */
    box-shadow: 0 6px 20px rgba(52, 199, 89, 0.25); /* Aligned with accent */
    background: var(--card-bg);
    padding: 1.2rem;
    transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.4s ease;
}

.login-logo:hover {
    transform: scale(1.12); /* Slightly more pronounced scaling */
    box-shadow: var(--shadow-glow), 0 8px 24px rgba(52, 199, 89, 0.35);
}

.login-title {
    background: var(--gradient-accent); /* Aligned with table gradients */
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 3.5rem;
    font-size: 3.2rem; /* Slightly larger */
    font-weight: 800;
    text-shadow: 0 2px 12px rgba(52, 199, 89, 0.5); /* Aligned with accent */
    letter-spacing: -0.02em;
    animation: fadeInSlideUp 0.8s ease-out forwards;
}

@keyframes fadeInSlideUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

form {
    display: flex;
    flex-direction: column;
    gap: 2.2rem; /* Slightly larger gap */
    width: 100%;
    max-width: 520px; /* Wider form for better spacing */
    margin: 0 auto;
}

.form-group {
    text-align: left;
    position: relative;
}

label {
    display: flex;
    align-items: center;
    gap: 0.7rem;
    margin-bottom: 0.9rem;
    color: var(--text-light);
    font-weight: 600;
    font-size: 1.15rem; /* Slightly larger for clarity */
    transition: color 0.3s ease;
}

label i {
    font-size: 1.4rem; /* Slightly larger icon */
    color: var(--primary);
    transition: color 0.3s ease, transform 0.3s ease;
}

label:hover i {
    color: var(--accent);
    transform: scale(1.1); /* Subtle icon animation */
}

input[type="text"],
input[type="password"] {
    width: 100%;
    padding: 1.3rem 1.6rem; /* Slightly more padding */
    border: 1px solid var(--border);
    border-radius: 1.2rem; /* More rounded */
    background-color: rgba(255, 255, 255, 0.12); /* Slightly brighter */
    color: var(--text-light);
    font-size: 1.1rem;
    outline: none;
    transition: border-color 0.3s ease, box-shadow 0.3s ease, background-color 0.3s ease;
}

input[type="text"]::placeholder,
input[type="password"]::placeholder {
    color: var(--text-muted);
    opacity: 0.85;
    font-weight: 400;
}

input[type="text"]:focus,
input[type="password"]:focus {
    border-color: var(--accent); /* Aligned with table accent */
    box-shadow: 0 0 0 4px rgba(52, 199, 89, 0.25), var(--shadow-glow); /* Aligned with table glow */
    background-color: rgba(255, 255, 255, 0.18);
}

input[type="text"]:focus + label i,
input[type="password"]:focus + label i {
    color: var(--accent);
    transform: scale(1.1);
}

button[type="submit"] {
    padding: 1.3rem 2.2rem; /* Slightly larger */
    background: var(--gradient-accent); /* Aligned with table gradients */
    color: var(--text-dark-contrast);
    border: none;
    border-radius: 1.2rem;
    cursor: pointer;
    font-weight: 700;
    font-size: 1.25rem; /* Slightly larger */
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1); /* Smoother easing */
    box-shadow: var(--shadow-soft);
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.9rem;
    margin-top: 2.5rem;
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
    background: rgba(255, 255, 255, 0.25);
    border-radius: 50%;
    transform: translate(-50%, -50%);
    transition: width 0.5s ease, height 0.5s ease;
}

button[type="submit"]:hover:not(:disabled)::after {
    width: 450px; /* Slightly larger ripple effect */
    height: 450px;
}

button[type="submit"]:hover:not(:disabled) {
    background: var(--gradient-accent-hover); /* Aligned with table hover gradients */
    transform: translateY(-5px) scale(1.02); /* More pronounced lift */
    box-shadow: var(--shadow-glow), 0 12px 36px rgba(52, 199, 89, 0.4);
}

button[type="submit"]:focus:not(:disabled) {
    outline: 3px solid var(--accent);
    outline-offset: 4px;
    box-shadow: var(--shadow-glow);
}

button[type="submit"]:disabled {
    background: rgba(52, 199, 89, 0.3); /* Aligned with accent */
    cursor: not-allowed;
    box-shadow: none;
    transform: none;
}

.spinner-small {
    border: 4px solid rgba(255, 255, 255, 0.3);
    border-top: 4px solid var(--accent); /* Aligned with accent */
    border-radius: 50%;
    width: 28px; /* Slightly larger */
    height: 28px;
    animation: spin 0.7s linear infinite; /* Slightly faster */
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.error-message {
    color: var(--danger);
    margin-top: 2.5rem;
    font-size: 1.15rem; /* Slightly larger */
    font-weight: 600;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.8rem;
    padding: 1.2rem;
    background-color: rgba(255, 77, 79, 0.2); /* Slightly more opaque */
    border-radius: 0.9rem;
    border: 1px solid rgba(255, 77, 79, 0.35);
    box-shadow: var(--shadow-soft);
    animation: fadeIn 0.4s ease-out;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(12px); }
    to { opacity: 1; transform: translateY(0); }
}

.error-message i {
    font-size: 1.5rem; /* Slightly larger */
}

.register-link {
    margin-top: 3.5rem;
    color: var(--text-muted);
    font-size: 1.1rem;
}

.register-link a {
    color: var(--accent);
    text-decoration: none;
    font-weight: 700;
    transition: color 0.3s ease, text-shadow 0.3s ease;
}

.register-link a:hover {
    color: var(--primary);
    text-shadow: 0 0 10px rgba(77, 182, 255, 0.6);
}

@media (prefers-reduced-motion: reduce) {
    .login-card::before,
    :global(body),
    .login-logo,
    .login-title,
    button[type="submit"],
    button[type="submit"]::after,
    .error-message {
        animation: none !important;
    }
    .login-card,
    .login-logo,
    button[type="submit"],
    input[type="text"],
    input[type="password"],
    label i,
    .register-link a {
        transition: none !important;
        transform: none !important;
    }
}

@media (max-width: 700px) {
    .login-container {
        padding: 2rem 1rem;
    }
    .login-card {
        padding: 3rem 2rem;
        max-width: 90vw;
        min-width: unset;
    }
    .login-title {
        font-size: 2.8rem;
    }
    form {
        max-width: 100%;
        gap: 1.8rem;
    }
    button[type="submit"] {
        padding: 1.1rem 1.8rem;
        font-size: 1.15rem;
    }
    .login-logo {
        width: 120px;
        height: 120px;
    }
}

@media (max-width: 400px) {
    .login-logo {
        width: 100px;
        height: 100px;
    }
    .login-title {
        font-size: 2.4rem;
    }
    .login-card {
        padding: 2.5rem 1.5rem;
    }
}
</style>