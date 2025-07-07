import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [sveltekit()],
  server: {
	proxy: {
	  '/api': {
		target: 'http://localhost:8000',
		changeOrigin: true,
		secure: false,
	  },
	  '/token': {
		target: 'http://localhost:8000',
		changeOrigin: true,
		secure: false,
	  },
	  '/register-user': {
		target: 'http://localhost:8000',
		changeOrigin: true,
		secure: false,
	  },
	},
  },
});
