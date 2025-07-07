<script>
  import BoardForm from '../../BoardForm.svelte';
  import { get_request } from '$lib/api';
  import { page } from '$app/stores';
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';

  let board = null;
  let loading = true;
  let error = '';

  let boardId;
  $: boardId = $page.params.id;

  onMount(async () => {
    try {
      board = await get_request(`/api/boards/${boardId}`);
      loading = false;
    } catch (err) {
      error = err.message || 'Failed to load board data.';
      loading = false;
    }
  });

  function handleSuccess() {
    goto('/dashboard');
  }
  function handleCancel() {
    goto('/dashboard');
  }
</script>

<div class="card board-form-container">
  <h2 class="text-2xl font-semibold text-text-light mb-4">Edit Board</h2>
  {#if loading}
    <div class="spinner"></div>
  {:else if error}
    <p class="error-message">{error}</p>
  {:else if board}
    <BoardForm board={board} mode="edit" on:success={handleSuccess} on:cancel={handleCancel} />
  {/if}
</div>
