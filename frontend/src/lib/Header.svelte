<script>
  import NavLink from './NavLink.svelte';
  import UserMenu from './UserMenu.svelte';
  import { auth } from '../stores/authStore.js';
  import { goto } from '$app/navigation';
</script>

<header class="header">
  <div class="logo" on:click={()=>goto('/')}>
    <span class="logored">Asteel</span>
    <span class="logoblue">Flash</span>
  </div>

  <nav>
    <NavLink href="/dashboard" label="Dashboard" />
    {#if $auth.userRole==='admin'}
      <NavLink href="/register" label="Register" />
    {/if}
  </nav>

  <div class="controls">
    {#if $auth.isAuthenticated}
      <UserMenu/>
    {:else}
      <NavLink href="/login" label="Login"/>
    {/if}
  </div>
</header>

<style>
  /* 1) Core Variables */
:root {
  --clr-bg-light: #ffffff;
  --clr-bg-dark:  #1e1f29;
  --clr-text:     #f8f8f2;
  --clr-text-alt: #6272a4;
  --clr-primary:  #8be9fd;
  --clr-accent:   #50fa7b;
  --clr-danger:   #ff5555;
  --radius:       0.6rem;
  --transition:   0.3s ease;
  --shadow-md:    0 8px 24px rgba(0,0,0,0.2);
}

html[data-theme="light"] {
  --clr-bg:      var(--clr-bg-light);
  --clr-text:    #2e2e2e;
  --clr-card:    rgba(255,255,255,0.9);
}
html[data-theme="dark"] {
  --clr-bg:      var(--clr-bg-dark);
  --clr-text:    var(--clr-text);
  --clr-card:    rgba(40,42,54,0.75);
}

body {
  background: var(--clr-bg);
  color: var(--clr-text);
  transition: background var(--transition), color var(--transition);
  margin:0; font-family: 'Inter', sans-serif;
}

/* 2) Header Layout & Glass */
.header {
  position: sticky; top:0; z-index:1000;
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  padding: 1rem 2rem;
  background: var(--clr-card);
  backdrop-filter: blur(16px);
  box-shadow: var(--shadow-md);
  transition: padding 0.2s, box-shadow 0.2s;
}
.header.shrink {
  padding: 0.6rem 2rem;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

/* 3) Logo Anim & Hover */
.logo {
  font-size: 1.8rem; font-weight: 800;
  cursor: pointer;
  display: inline-flex;
  opacity: 0;
  animation: fadeIn 0.6s forwards 0.2s;
}
.logo .logored { color: var(--clr-danger); }
.logo .logoblue { color: var(--clr-primary); margin-left: 0.3rem; }
.logo:hover { transform: scale(1.05); transition: transform var(--transition); }

@keyframes fadeIn {
  to { opacity: 1; }
}

/* 4) Nav Links with Sliding Underline */
nav {
  display: flex; gap: 1.6rem; justify-self: center;
}
.nav-link {
  position: relative;
  padding: 0.5rem 1rem;
  border-radius: var(--radius);
  font-weight: 600;
  color: var(--clr-text);
  text-decoration: none;
  transition: background var(--transition);
}
.nav-link::after {
  content: '';
  position: absolute; bottom: 0; left: 50%;
  width: 0; height: 2px;
  background: var(--clr-accent);
  border-radius: 1px;
  transition: width var(--transition), left var(--transition);
}
.nav-link:hover {
  background: rgba(80,250,123,0.1);
}
.nav-link:hover::after,
.nav-link[aria-current="page"]::after {
  width: 70%;
  left: 15%;
}

/* 5) Controls: Search, Bell, Avatar, Theme */
.controls {
  display: flex; align-items: center; gap: 1rem; justify-self: end;
}
/* Quick-search icon */
.control-btn {
  background: none; border: none; cursor: pointer;
  font-size: 1.4rem; color: var(--clr-text-alt);
  transition: color var(--transition), transform 0.2s;
}
.control-btn:hover {
  color: var(--clr-text);
  transform: scale(1.2);
}

/* Notification bell badge */
.bell {
  position: relative;
}
.bell .badge {
  position: absolute; top: -4px; right: -4px;
  background: var(--clr-danger);
  width: 0.6rem; height: 0.6rem;
  border-radius: 50%;
  animation: pulse 1.5s infinite;
}
@keyframes pulse {
  0%,100% { transform: scale(1); opacity: 1; }
  50%     { transform: scale(1.3); opacity: 0.6; }
}

/* Avatar dropdown container */
.avatar-container {
  position: relative;
  width: 2.4rem; height: 2.4rem;
  background: linear-gradient(135deg, var(--clr-primary), var(--clr-accent));
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; overflow: hidden;
  transition: transform 0.2s;
}
.avatar-container:hover { transform: scale(1.1); }
.avatar-container .dropdown {
  position: absolute; top: 120%; right: 0;
  background: var(--clr-card);
  backdrop-filter: blur(12px);
  border-radius: var(--radius);
  box-shadow: var(--shadow-md);
  overflow: hidden;
  opacity: 0; pointer-events: none;
  transition: opacity var(--transition);
}
.avatar-container.open .dropdown {
  opacity: 1; pointer-events: auto;
}

/* 6) Mobile menu toggle */
.mobile-menu-btn {
  display: none;
  background: none; border: none;
  font-size: 1.6rem; cursor: pointer;
}
@media (max-width:900px) {
  .header { grid-template-columns: auto auto; }
  nav { display: none; }
  nav.open { display: flex; position: absolute; top:100%; left:0;
    flex-direction: column; width:100%; background: var(--clr-card);
    padding: 1rem 0; box-shadow: var(--shadow-md);
  }
  .mobile-menu-btn { display: block; }
}

/* 7) Shrink on scroll (JS hook) */


</style>
