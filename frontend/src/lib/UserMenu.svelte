<script>
  import { auth, logout } from '../stores/authStore.js';
  let open = false;
  function toggle() { open = !open; }
  function doLogout() { logout(); }
</script>

<div class="user-menu">
  <div class="avatar" on:click={toggle}>
    <i class="ri-user-3-fill"></i>
  </div>
  {#if open}
    <div class="dropdown" transition:fade>
      <div class="username">{$auth.username}</div>
      <button on:click={doLogout}>Logout</button>
    </div>
  {/if}
</div>

<style>
  /* Avatar style */
  .avatar {
    background: linear-gradient(135deg, var(--primary), var(--accent));
    width: 3rem; height: 3rem; /* Slightly larger avatar */
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    cursor: pointer;
    box-shadow: var(--shadow);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
  }
  
  /* Avatar hover effect */
  .avatar:hover {
    transform: scale(1.1); /* Slightly zoom in the avatar */
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1); /* Add a stronger shadow */
  }

  /* Dropdown menu styling */
  .dropdown {
    position: absolute;
    top: 3.5rem; /* Adjusted for better spacing */
    right: 0;
    background: var(--card-background);
    padding: 1.2em 1.5em; /* Added padding for better content spacing */
    border-radius: 1em; /* More rounded corners for a softer look */
    box-shadow: var(--shadow-medium);
    display: flex; flex-direction: column;
    gap: 1rem;
    animation: dropdownFadeIn 0.3s ease-in-out;
  }

  /* Dropdown fade-in animation */
  @keyframes dropdownFadeIn {
    from { opacity: 0; transform: translateY(-10px); }
    to { opacity: 1; transform: translateY(0); }
  }

  /* Username style */
  .username {
    font-size: 1.1rem; /* Slightly larger font */
    font-weight: 600;
    color: var(--text-light);
    text-align: center;
    margin-bottom: 0.5rem; /* Spacing between username and logout button */
  }

  /* Button styling */
  .dropdown button {
    background: var(--danger);
    color: #fff;
    border: none;
    padding: 0.8em 1.5em; /* Increased padding for a larger button */
    border-radius: 0.5em;
    cursor: pointer;
    font-size: 1rem;
    font-weight: 600;
    text-align: center;
    transition: background 0.3s ease, transform 0.2s ease;
  }

  /* Button hover effect */
  .dropdown button:hover {
    background: var(--danger-dark);
    transform: scale(1.05); /* Slight zoom-in effect */
  }

  /* Button focus effect for better accessibility */
  .dropdown button:focus {
    outline: 3px solid var(--primary-light);
    outline-offset: 4px;
  }
</style>
