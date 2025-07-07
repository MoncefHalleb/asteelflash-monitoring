<script>
  import { auth, logout } from '../stores/authStore.js';
  import { goto, afterNavigate, beforeNavigate } from '$app/navigation';
  import { onMount } from 'svelte';
  import { tick } from 'svelte';
  import { page } from '$app/stores';

  let mobileMenuOpen = false;
  let loading = false;

  // Redirect if not authenticated
  $: if (
    !$auth.isAuthenticated &&
    typeof window !== 'undefined' &&
    !['/login', '/register'].includes($page.url.pathname)
  ) {
    goto('/login');
  }

  function handleLogout() {
    logout();
    mobileMenuOpen = false;
  }

  // Loading indicator on navigation
  beforeNavigate(() => { loading = true; });
  afterNavigate(() => { loading = false; });

  function toggleMobileMenu() {
    mobileMenuOpen = !mobileMenuOpen;
  }
</script>

<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/remixicon@4.2.0/fonts/remixicon.min.css">

<header class="main-header">
  <div class="header-left">
    <a href="/" class="app-title-link" aria-label="Home">
<div style="font-family: 'Inter', sans-serif; font-size: 3em; font-weight: 700; color: #f8f8f2; letter-spacing: -0.02em; display: flex; align-items: center;">
  <span style="color: #ff5555;">Asteel</span>
  <span style="font-size: 0.8em; color: #6272a4; margin: 0 0.4em;">|</span>
  <span style="color: #8be9fd; font-weight: 800;">Flash</span>
</div>
</a>
  </div>
  <nav class="main-nav" aria-label="Main navigation">
    <button class="mobile-menu-btn" aria-label="Toggle menu" on:click={toggleMobileMenu}>
      <i class="ri-menu-line"></i>
    </button>
    <ul class:open={mobileMenuOpen}>
      {#if $auth.isAuthenticated}
        <li><a href="/dashboard" class="nav-link" aria-current={$page.url.pathname === '/dashboard' ? 'page' : undefined}>Dashboard</a></li>
        {#if $auth.userRole === 'admin'}
          <li><a href="/admin" class="nav-link" aria-current={$page.url.pathname === '/admin' ? 'page' : undefined}>Admin Panel</a></li>
          {#if $auth.isAuthenticated && $auth.userRole === 'admin'}
            <li><a href="/register" class="nav-link" aria-current={$page.url.pathname === '/register' ? 'page' : undefined}>Register</a></li>
          {/if}
        {/if}
      {:else}
        <li><a href="/login" class="nav-link" aria-current={$page.url.pathname === '/login' ? 'page' : undefined}>Login</a></li>
      {/if}
    </ul>
  </nav>
  <div class="user-info">
    {#if $auth.isAuthenticated}
      <div class="avatar-container">
        <div class="avatar"></div>
          <i class="ri-user-3-fill"></i>
        </div>
        <div class="user-details">
          <span class="welcome-text">
            <span class="greeting">Welcome,</span>
            <span class="username">{$auth.username}</span>
            <span class="role-badge" data-role="{$auth.userRole}">
              {$auth.userRole}
            </span>
          </span>
        </div>
      
      <button on:click={handleLogout} class="logout-button" aria-label="Logout">
        <i class="ri-logout-box-r-line" style="margin-right: 0.5em;"></i>Logout
      </button>
    {/if}
  </div>

  <!-- Debug output for auth store -->
</header>

{#if loading}
  <div class="loading-bar"></div>
{/if}

<main>
  <slot />
</main>

<style>
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
        background-image: url('/images.png'); /* Change this to your desired image */

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
    background-image: url('/images.png'); /* Change this to your desired image */
    background-position: center center;
    background-size: cover; /* or 50% or contain */
    background-repeat: no-repeat;
    opacity: 0.08;
    filter: grayscale(100%) brightness(60%);
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
  .main-header {
    background-color: var(--card-bg);
    padding: 1.2rem 2.5rem;
    display: flex;
    justify-content: space-between;
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
  .main-nav {
    position: relative;
  }
  .main-nav ul {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    gap: 1.8rem;
    transition: max-height 0.3s;
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
  .mobile-menu-btn {
    display: none;
    background: none;
    border: none;
    color: var(--text-light);
    font-size: 2rem;
    cursor: pointer;
    margin-right: 1rem;
  }
  
    .avatar-container {
      display: flex;
      align-items: center;
      gap: 1rem;
      background: rgba(68, 71, 90, 0.35);
      padding: 0.5rem 1rem;
      border-radius: 2rem;
      box-shadow: 0 2px 8px rgba(139, 233, 253, 0.08);
      transition: background 0.2s;
    }
    .avatar {
      width: 2.5rem;
      height: 2.5rem;
      background: linear-gradient(135deg, var(--primary) 60%, var(--accent) 100%);
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #282a36;
      font-size: 1.5rem;
      font-weight: bold;
      box-shadow: 0 2px 8px rgba(139, 233, 253, 0.15);
    }
    .user-details {
      display: flex;
      flex-direction: column;
      justify-content: center;
    }
    .welcome-text {
      font-size: 1.05rem;
      color: var(--text-dark-contrast);
      white-space: nowrap;
      display: flex;
      align-items: center;
      gap: 0.5em;
    }
    .greeting {
      color: var(--primary-dark);
      font-weight: 400;
      margin-right: 0.2em;
    }
    .username {
      color: var(--primary);
      font-weight: 700;
      margin-right: 0.3em;
      letter-spacing: 0.01em;
    }
    .role-badge {
      display: inline-block;
      padding: 0.18em 0.7em;
      border-radius: 1em;
      font-size: 0.85em;
      font-weight: 700;
      text-transform: capitalize;
      margin-left: 0.2em;
      background: linear-gradient(90deg, #44476a 60%, var(--primary-dark) 100%);
      color: #fff;
      letter-spacing: 0.02em;
      box-shadow: 0 1px 4px rgba(139, 233, 253, 0.08);
      border: 1px solid rgba(139, 233, 253, 0.15);
    }
    .role-badge[data-role="admin"] {
      background: linear-gradient(90deg, var(--danger) 60%, #ff79c6 100%);
      color: #fff;
      border: 1px solid #ff5555;
    }
    .role-badge[data-role="user"] {
      background: linear-gradient(90deg, var(--primary) 60%, var(--accent) 100%);
      color: #282a36;
      border: 1px solid var(--primary);
    }
    .logout-button {
      margin-left: 1.2rem;
      display: flex;
      align-items: center;
      gap: 0.3em;
    }
    @media (max-width: 900px) {
      .avatar-container {
        padding: 0.4rem 0.7rem;
        gap: 0.7rem;
      }
      .logout-button {
        margin-left: 0.5rem;
      }
    }
  
  /* Responsive styles */
  @media (max-width: 900px) {
    .main-header {
      flex-direction: column;
      align-items: stretch;
      padding: 1rem 1.2rem;
    }
    .main-nav ul {
      flex-direction: column;
      gap: 0.5rem;
      background: var(--card-bg);
      position: absolute;
      top: 100%;
      left: 0;
      right: 0;
      max-height: 0;
      overflow: hidden;
      box-shadow: var(--shadow);
      border-radius: 0 0 0.6rem 0.6rem;
    }
    .main-nav ul.open {
      max-height: 400px;
      padding: 1rem 0;
    }
    .mobile-menu-btn {
      display: inline-block;
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