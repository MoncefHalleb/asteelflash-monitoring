<script>
  import Header from '$lib/Header.svelte';
  // in your root layout component
  import { onMount } from 'svelte';
  let header;
  onMount(() => {
    const onScroll = () => {
      header.classList.toggle('shrink', window.scrollY > 20);
    };
    window.addEventListener('scroll', onScroll);
    return () => window.removeEventListener('scroll', onScroll);
  });
</script>

<Header/>
<main>
  <slot/>
</main>
