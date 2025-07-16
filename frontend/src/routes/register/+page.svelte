<script>
  import { post } from '$lib/api';
  let username = '';
  let password = '';
  let role = 'user';
  let message = '';
  let isError = false;
  let isLoading = false;

  async function handleSubmit() {
    message = '';
    isError = false;
    isLoading = true;
    try {
      const response = await post('/register-user', { username, password, role }, 'application/json');
      message = response.message || 'User added successfully!';
      username = '';
      password = '';
      role = 'user';
    } catch (error) {
      message = error.message || 'Failed to add user.';
      isError = true;
    } finally {
      isLoading = false;
    }
  }
</script>

<div class="login-container">
  <div class="login-card">
    <img src="/images.png" alt="AsteelFlash Logo" class="login-logo" />
    <h1 class="login-title">Add New User</h1>
    <form on:submit|preventDefault={handleSubmit}>
      <div class="form-group">
        <label for="username"><i class="ri-user-line"></i> Username</label>
        <input type="text" id="username" bind:value={username} required autocomplete="off" placeholder="Enter a username" />
      </div>

      <div class="form-group">
        <label for="password"><i class="ri-lock-line"></i> Password</label>
        <input type="password" id="password" bind:value={password} required autocomplete="new-password" placeholder="Enter a password" />
      </div>

    <div class="form-group">
      <label for="role"><i class="ri-shield-user-line" color="black"></i> Role</label>
      <select id="role" bind:value={role} style="color: black;">
        <option value="user">User</option>
        <option value="admin">Admin</option>
      </select>
    </div>

      <button type="submit" disabled={isLoading}>
        {#if isLoading}
          <div class="spinner-small"></div>
          Creating...
        {:else}
          <i class="ri-user-add-line"></i> Add User
        {/if}
      </button>
    </form>

    {#if message}
      <p class={isError ? 'error-message' : 'success-message'}>
        <i class={isError ? 'ri-error-warning-fill' : 'ri-check-line'}></i>
        {message}
      </p>
    {/if}
  </div>
</div>

<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
  @import url('https://cdn.jsdelivr.net/npm/remixicon@4.3.0/fonts/remixicon.min.css');
  :global(body) {
    margin: 0;
    font-family: 'Inter', sans-serif;
    background-color: #12141c;
    color: #f0f2f5;
    line-height: 1.7;
    min-height: 90vh;
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
    background-color: rgba(28, 30, 41, 0.85);
    border-radius: 1.5rem;
    border: 1px solid rgba(77, 182, 255, 0.2);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35);
    backdrop-filter: blur(12px);
    padding: 3.5rem;
    max-width: 700px;
    width: 100%;
    text-align: center;
    display: flex;
    flex-direction: column;
    align-items: center;
}
  .login-logo {
    width: 120px;
    height: 120px;
    object-fit: contain;
    margin-bottom: 2rem;
    border-radius: 1.2rem;
    box-shadow: 0 4px 16px rgba(77, 182, 255, 0.2);
    background: #1c1e29;
    padding: 1rem;
  }
  .login-title {
    background: linear-gradient(135deg, #4db6ff, #34c759);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 2.5rem;
    font-size: 2.8rem;
    font-weight: 800;
    letter-spacing: -0.015em;
  }
  form {
    display: flex;
    flex-direction: column;
    gap: 1.75rem;
    width: 100%;
    max-width: 420px;
  }
  .form-group label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
    color: #f0f2f5;
    font-weight: 600;
    font-size: 1.05rem;
  }
  input, select {
    width: 100%;
    padding: 1.1rem 1.4rem;
    border: 1px solid rgba(77, 182, 255, 0.2);
    border-radius: 0.85rem;
    background-color: rgba(255, 255, 255, 0.08);
    color: #f0f2f5;
    font-size: 1.1rem;
  }
  input::placeholder {
    color: #a0a5c0;
  }
  button {
    padding: 1.1rem 1.8rem;
    background: linear-gradient(135deg, #4db6ff 0%, #34c759 100%);
    color: #1e1e2e;
    border: none;
    border-radius: 0.85rem;
    font-weight: 700;
    font-size: 1.2rem;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.75rem;
  }
  .spinner-small {
    border: 3px solid rgba(255, 255, 255, 0.3);
    border-top: 3px solid #f0f2f5;
    border-radius: 50%;
    width: 20px;
    height: 20px;
    animation: spin 1s linear infinite;
  }
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
  .success-message, .error-message {
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
    color: #34c759;
    background-color: rgba(52, 199, 89, 0.1);
    border: 1px solid rgba(52, 199, 89, 0.3);
  }
  .error-message {
    color: #ff4d4f;
    background-color: rgba(255, 77, 79, 0.1);
    border: 1px solid rgba(255, 77, 79, 0.3);
  }
</style>