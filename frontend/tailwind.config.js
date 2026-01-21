/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                midnight: '#0f172a', // Deep midnight blue
                accent: '#38bdf8',   // Light blue accent
            }
        },
    },
    plugins: [],
}
