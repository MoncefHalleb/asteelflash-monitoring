<script>
  import BoardForm from '../BoardForm.svelte';
  import { goto } from '$app/navigation';

  function handleSuccess() {
    goto('/dashboard');
  }
  function handleCancel() {
    goto('/dashboard');
  }
</script>

<div class="card board-form-container">
  <BoardForm mode="create" on:success={handleSuccess} on:cancel={handleCancel} />
</div>