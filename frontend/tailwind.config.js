/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: '#0070f3',
      },
    },
  },
  plugins: [require('daisyui')],
  daisyui: {
    themes: [
      {
        light: {
          primary: '#0070f3',
          'primary-focus': '#0060df',
          'primary-content': '#ffffff',
          secondary: '#6c757d',
          accent: '#37cdbe',
          neutral: '#3d4451',
          'base-100': '#ffffff',
          'base-200': '#f8f9fa',
          'base-300': '#e9ecef',
        },
        dark: {
          primary: '#3b82f6',
          'primary-focus': '#2563eb',
          'primary-content': '#ffffff',
          secondary: '#6c757d',
          accent: '#37cdbe',
          neutral: '#3d4451',
          'base-100': '#1f2937',
          'base-200': '#111827',
          'base-300': '#0f172a',
        }
      },
      "corporate",
      "business"
    ],
    darkTheme: 'dark',
  },
};
