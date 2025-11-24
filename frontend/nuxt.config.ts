import tailwindcss from '@tailwindcss/vite';
// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
	compatibilityDate: '2025-07-15',
	devtools: { enabled: true },
	modules: ['@nuxt/ui'],
	css: ['~/assets/css/main.css'],
	vite: { plugins: [tailwindcss()] },
	runtimeConfig: {
		// Private keys are only available on the server
		apiBase: 'http://ns_backend:8000',
		// Public keys that are exposed to the client
		public: {
			apiBase: 'http://localhost:8000',
		},
	},
});
