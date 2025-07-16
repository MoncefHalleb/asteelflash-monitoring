<script>
  export let href;
  export let label;
  import { page } from '$app/stores';
</script>

<a
  href={href}
  class="nav-link"
  aria-current={$page.url.pathname === href ? 'page' : undefined}
  on:mouseenter
  on:mouseleave
>
  {label}
</a>

<style>
  .nav-link {
    position: relative;
    padding: 0.75em 1.2em;
    border-radius: 0.5em;
    text-decoration: none;
    font-weight: 600;
    transition: transform 0.2s;
  }
  .nav-link::after {
    content: '';
    position: absolute;
    bottom: 0.2em;
    left: 50%;
    width: 0;
    height: 2px;
    background: var(--accent);
    transition: width 0.3s, left 0.3s;
  }
  .nav-link:hover {
    transform: translateY(-2px);
  }
  .nav-link:hover::after,
  .nav-link[aria-current='page']::after {
    width: 80%;
    left: 10%;
  }
</style>
