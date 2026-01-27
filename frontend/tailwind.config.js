/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                background: '#0c0a09', // Stone 950 (Warm Dark Base)
                surface: '#1c1917',    // Stone 900 (Cards)
                primary: '#a78bfa',    // Violet 400 (Creative/Calm)
                'primary-hover': '#8b5cf6', // Violet 500
                secondary: '#34d399',  // Emerald 400 (Medical Accent)
                accent: '#f472b6',     // Pink 400 (Vitality/Pop)
                'glass-border': 'rgba(255, 255, 255, 0.08)',
                success: '#34d399',    // Emerald
                warning: '#fbbf24',    // Amber
                error: '#f87171',      // Red
            },
            animation: {
                'fade-in': 'fadeIn 0.5s ease-out forwards',
                'float': 'float 20s ease-in-out infinite',
                'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
                'heartbeat': 'heartbeat 3s ease-in-out infinite',
            },
            keyframes: {
                fadeIn: {
                    '0%': { opacity: '0', transform: 'translateY(10px)' },
                    '100%': { opacity: '1', transform: 'translateY(0)' },
                },
                float: {
                    '0%, 100%': { transform: 'translateY(0) scale(1)' },
                    '50%': { transform: 'translateY(-20px) scale(1.05)' },
                },
                heartbeat: {
                    '0%, 100%': { transform: 'scale(1)' },
                    '50%': { transform: 'scale(1.03)' },
                }
            }
        },
    },
    plugins: [],
}
