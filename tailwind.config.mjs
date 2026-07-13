/** @type {import('tailwindcss').Config} */
export default {
	content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
	theme: {
		extend: {
			colors: {
				// Brand Beriklan.co.id
				primary: '#0f1e3d',      // Deep Navy — text utama & bg gelap
				'primary-2': '#1a2f5c',  // Navy medium
				accent: '#f59e0b',       // Amber — CTA & highlight metric
				'accent-2': '#fbbf24',   // Amber light
				teal: '#0ea5e9',         // Sky blue — supporting
				green: '#10b981',        // Emerald — success/growth
				beige: '#f8f5f0',        // Warm bg
				'soft': '#f5f7fb',       // Soft panel bg
				ink: '#0b1426',          // Heading strong
				muted: '#5b6478',        // Body muted
			},
			fontFamily: {
				sans: ['"Plus Jakarta Sans Variable"', '"Inter Variable"', 'system-ui', 'sans-serif'],
				display: ['"Plus Jakarta Sans Variable"', '"Inter Variable"', 'system-ui', 'sans-serif'],
				mono: ['"Geist Mono Variable"', 'ui-monospace', 'monospace'],
			},
			boxShadow: {
				'soft': '0 1px 2px rgba(15,30,61,.04), 0 8px 24px rgba(15,30,61,.06)',
				'pop': '0 12px 40px -8px rgba(15,30,61,.18)',
			},
		},
	},
	plugins: [],
}
