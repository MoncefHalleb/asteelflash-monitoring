<script>
    import { auth, logout } from '../stores/authStore.js';
    import { goto, afterNavigate, beforeNavigate } from '$app/navigation';
    import { onMount } from 'svelte';
    import { tick } from 'svelte';
    import { page } from '$app/stores';

    let mobileMenuOpen = false;
    let loading = false;

    // Redirect if not authenticated (using $page.url.pathname for current route)
    $: if (
        !$auth.isAuthenticated &&
        typeof window !== 'undefined' &&
        !['/login', '/register'].includes($page.url.pathname)
    ) {
        goto('/login');
    }

    function handleLogout() {
        logout();
        mobileMenuOpen = false; // Close menu on logout
    }

    // Loading indicator on navigation
    beforeNavigate(() => { loading = true; });
    afterNavigate(() => {
        loading = false;
        mobileMenuOpen = false; // Close mobile menu after navigation
    });

    function toggleMobileMenu() {
        mobileMenuOpen = !mobileMenuOpen;
    }

    // Close mobile menu if clicked outside or on Escape key
    function handleClickOutside(event) {
        const header = document.querySelector('.main-header');
        if (mobileMenuOpen && header && !header.contains(event.target)) {
            mobileMenuOpen = false;
        }
    }

    function handleKeydown(event) {
        if (mobileMenuOpen && event.key === 'Escape') {
            mobileMenuOpen = false;
        }
    }

    // Add global event listeners on mount
    onMount(() => {
        document.addEventListener('click', handleClickOutside);
        document.addEventListener('keydown', handleKeydown);

        // Cleanup event listeners on component unmount
        return () => {
            document.removeEventListener('click', handleClickOutside);
            document.removeEventListener('keydown', handleKeydown);
        };
    });
</script>

<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/remixicon@4.2.0/fonts/remixicon.min.css">

<header class="main-header">
    <div class="header-left">
        <a href="/" class="app-title-link" aria-label="Home">
            <h3 class="app-title">ASTEELFLASH App</h3>
        </a>
    </div>

    <button class="mobile-menu-btn" aria-label="Toggle menu" on:click={toggleMobileMenu}>
        {#if mobileMenuOpen}
            <i class="ri-close-line"></i>
        {:else}
            <i class="ri-menu-line"></i>
        {/if}
    </button>

    <nav class="main-nav" aria-label="Main navigation">
        <ul class="desktop-nav"> {#if $auth.isAuthenticated}
                <li><a href="/dashboard" class="nav-link" aria-current={$page.url.pathname === '/dashboard' ? 'page' : undefined}>Dashboard</a></li>
                {#if $auth.userRole === 'admin'}
                    <li><a href="/admin" class="nav-link" aria-current={$page.url.pathname === '/admin' ? 'page' : undefined}>Admin Panel</a></li>
                {/if}
            {:else}
                <li><a href="/login" class="nav-link" aria-current={$page.url.pathname === '/login' ? 'page' : undefined}>Login</a></li>
                <li><a href="/register" class="nav-link" aria-current={$page.url.pathname === '/register' ? 'page' : undefined}>Register</a></li>
            {/if}
        </ul>
    </nav>

    <div class="user-info">
        {#if $auth.isAuthenticated}
            <span class="welcome-text">Welcome, {$auth.username} ({$auth.userRole})!</span>
            <button on:click={handleLogout} class="logout-button" aria-label="Logout">Logout</button>
        {/if}
    </div>

    <div class="mobile-menu-overlay" class:open={mobileMenuOpen}>
        <nav class="mobile-nav" aria-label="Mobile navigation">
            <ul>
                {#if $auth.isAuthenticated}
                    <li><a href="/dashboard" class="nav-link" on:click={toggleMobileMenu} aria-current={$page.url.pathname === '/dashboard' ? 'page' : undefined}>Dashboard</a></li>
                    {#if $auth.userRole === 'admin'}
                        <li><a href="/admin" class="nav-link" on:click={toggleMobileMenu} aria-current={$page.url.pathname === '/admin' ? 'page' : undefined}>Admin Panel</a></li>
                    {/if}
                    <li><button on:click={handleLogout} class="logout-button">Logout</button></li>
                {:else}
                    <li><a href="/login" class="nav-link" on:click={toggleMobileMenu} aria-current={$page.url.pathname === '/login' ? 'page' : undefined}>Login</a></li>
                    <li><a href="/register" class="nav-link" on:click={toggleMobileMenu} aria-current={$page.url.pathname === '/register' ? 'page' : undefined}>Register</a></li>
                {/if}
            </ul>
        </nav>
    </div>
</header>

{#if loading}
    <div class="loading-bar"></div>
{/if}

<main>
    <slot />
</main>

<style>
    /*
    * IMPORTANT:
    * The :root variables, global font imports, and global body styles
    * should ideally be defined ONCE in src/app.css.
    * I'm including them here for self-containment in this example,
    * but for a real SvelteKit app, avoid duplication.
    */
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

    /* Header Styling */
    .main-header {
        background-color: var(--card-bg);
        padding: 1.2rem 2.5rem;
        display: flex;
        justify-content: space-between; /* Distribute items horizontally */
        align-items: center;
        border-bottom: var(--border);
        box-shadow: var(--shadow);
        backdrop-filter: blur(var(--glass-blur));
        -webkit-backdrop-filter: blur(var(--glass-blur-webkit));
        color: var(--text-light);
        position: sticky;
        top: 0;
        z-index: 1000;
        transition: background-color 0.3s ease, box-shadow 0.3s ease;
    }
    .main-header:hover {
        box-shadow: 0 10px 35px 0 rgba(0, 0, 0, 0.5);
    }
    .app-title-link {
        text-decoration: none;
        color: inherit;
    }
    .app-title {
        margin: 0;
        color: var(--primary);
        font-size: 1.8rem;
        font-weight: 800;
        letter-spacing: 0.04em;
        text-shadow: 0 0 8px rgba(139, 233, 253, 0.3);
    }

    /* Desktop Navigation */
    .main-nav .desktop-nav {
        list-style: none;
        margin: 0;
        padding: 0;
        display: flex; /* Always flex for desktop */
        gap: 1.8rem;
    }

    .nav-link {
        color: var(--text-light);
        text-decoration: none;
        font-weight: 600;
        padding: 0.75rem 1.25rem;
        border-radius: 0.6rem;
        transition: background-color 0.3s, color 0.3s, transform 0.2s;
        position: relative;
        overflow: hidden;
        display: block; /* Ensure full clickable area for mobile links */
    }
    .nav-link::before {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 3px;
        background-color: var(--accent);
        transform: translateX(-100%);
        transition: transform 0.3s;
    }
    .nav-link:hover::before,
    .nav-link[aria-current="page"]::before {
        transform: translateX(0);
    }
    .nav-link:hover,
    .nav-link[aria-current="page"] {
        background-color: rgba(80, 250, 123, 0.1);
        color: var(--accent);
        transform: translateY(-2px);
    }

    .user-info {
        display: flex;
        align-items: center;
        gap: 1.2rem;
    }
    .welcome-text {
        font-size: 0.95rem;
        color: var(--text-dark-contrast);
        white-space: nowrap;
    }
    .logout-button {
        background: linear-gradient(90deg, var(--danger) 0%, #ff79c6 100%);
        border: none;
        color: var(--text-light);
        padding: 0.75rem 1.25rem;
        border-radius: 0.6rem;
        cursor: pointer;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.3s;
        box-shadow: 0 4px 12px rgba(255, 85, 85, 0.2);
    }
    .logout-button:hover {
        background: linear-gradient(90deg, #ff79c6 0%, var(--danger) 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(255, 85, 85, 0.3);
    }

    /* Mobile Menu Button */
    .mobile-menu-btn {
        background: none;
        border: none;
        color: var(--text-light);
        font-size: 2rem;
        cursor: pointer;
        display: none; /* Hidden by default, shown on mobile */
        order: 2; /* Position it between app-title and user-info on mobile */
        margin-left: auto; /* Push it to the right on desktop, or if it's the middle element */
    }

    /* Mobile Menu Overlay */
    .mobile-menu-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.7); /* Dim background */
        backdrop-filter: blur(var(--glass-blur));
        -webkit-backdrop-filter: blur(var(--glass-blur-webkit));
        z-index: 999; /* Below header, but above content */
        display: flex;
        justify-content: flex-end; /* Push menu to the right */
        transform: translateX(100%); /* Start off-screen to the right */
        transition: transform 0.3s ease-in-out;
    }

    .mobile-menu-overlay.open {
        transform: translateX(0); /* Slide in */
    }

    .mobile-nav {
        width: 70%; /* Adjust width as needed */
        max-width: 300px; /* Max width for larger screens */
        background-color: var(--card-bg);
        border-left: var(--border);
        box-shadow: var(--shadow);
        padding: 2rem 1.5rem;
        overflow-y: auto; /* Scroll if content overflows */
        display: flex;
        flex-direction: column;
        align-items: flex-start; /* Align text to left */
    }

    .mobile-nav ul {
        list-style: none;
        margin: 0;
        padding: 0;
        width: 100%;
        display: flex;
        flex-direction: column;
        gap: 1rem; /* Space between mobile links */
    }

    .mobile-nav .nav-link,
    .mobile-nav .logout-button {
        width: calc(100% - 2.5rem); /* Account for padding */
        text-align: left; /* Align text to left in mobile menu */
        font-size: 1.1rem; /* Slightly larger text for readability */
        padding: 1rem 1.25rem;
    }

    .mobile-nav .logout-button {
        margin-top: 1rem; /* Space from last link */
    }

    /* Responsive styles */
    @media (max-width: 900px) {
        .main-header {
            flex-wrap: wrap; /* Allow items to wrap */
            justify-content: space-between; /* Distribute items */
            padding: 1rem 1.2rem; /* Adjusted padding for smaller screens */
        }
        .header-left {
            flex-grow: 1; /* Allow logo to take available space */
        }
        .user-info {
            order: 3; /* Move user info to the end on small screens */
            width: 100%; /* Take full width */
            justify-content: center; /* Center user info and logout button */
            margin-top: 0.8rem; /* Space from menu toggle */
        }
        .user-info .welcome-text {
            font-size: 0.85rem; /* Smaller font on mobile */
        }
        .main-nav .desktop-nav {
            display: none; /* Hide desktop navigation */
        }
        .mobile-menu-btn {
            display: block; /* Show mobile menu button */
            margin-left: 1rem; /* Space between logo and button */
            margin-right: 0;
        }
        .app-title {
            font-size: 1.5rem; /* Smaller title on mobile */
        }
    }

    main {
        padding: 20px;
        padding-top: 20px;
    }

    /* Loading bar */
    .loading-bar {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 4px;
        background: linear-gradient(90deg, var(--primary), var(--accent));
        z-index: 2000;
        animation: loading-bar 1s linear infinite;
    }
    @keyframes loading-bar {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
</style>