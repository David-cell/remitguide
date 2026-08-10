/** @type {import('tailwindcss').Config} */
// Template = code.html (Swiss editorial). Tokens mirror code.html's tailwind.config
// exactly so its utility classes (surface-variant, secondary, headline-display, page-margin…)
// compile from the generated HTML. Content scanned from HTML + build script.
module.exports = {
  darkMode: 'class',
  content: [
    './index.html',
    './*.html',
    './blog/*.html',
    './build_site.py',
    './brutal.css'
  ],
  theme: {
    extend: {
      colors: {
        // ---- code.html palette (exact) ----
        'background': '#fbf9f4',
        'surface': '#fbf9f4',
        'surface-dim': '#dbdad5',
        'surface-bright': '#fbf9f4',
        'surface-variant': '#e4e2dd',
        'surface-container': '#f0eee9',
        'surface-container-low': '#f5f3ee',
        'surface-container-lowest': '#ffffff',
        'surface-container-high': '#eae8e3',
        'surface-container-highest': '#e4e2dd',
        'surface-tint': '#5f5e5e',
        'on-surface': '#1b1c19',
        'on-surface-variant': '#444748',
        'on-background': '#1b1c19',
        'primary': '#1b1c19',
        'on-primary': '#fbf9f4',
        'primary-container': '#1c1b1b',
        'primary-fixed': '#e5e2e1',
        'primary-fixed-dim': '#c8c6c5',
        'on-primary-container': '#858383',
        'secondary': '#5e5e5e',
        'secondary-fixed': '#e4e2e2',
        'secondary-fixed-dim': '#c7c6c6',
        'secondary-container': '#e1dfdf',
        'on-secondary': '#ffffff',
        'on-secondary-container': '#636262',
        'outline': '#747878',
        'outline-variant': '#c4c7c7',
        'error': '#ba1a1a',
        'on-error': '#ffffff',
        'error-container': '#ffeceb',
        'on-error-container': '#ba1a1a',
        // ---- remit aliases kept for backward compat ----
        'brutalist-yellow': '#ba1a1a',
        'swiss-accent': '#ba1a1a',
        'cyber-green': '#ba1a1a'
      },
      borderRadius: {
        DEFAULT: '0.25rem',
        lg: '0.5rem',
        xl: '0.75rem',
        full: '9999px'
      },
      spacing: {
        base: '4px',
        'gap-md': '2.5rem',
        'gap-lg': '4.5rem',
        'gap-sm': '1.25rem',
        'gap-xs': '0.75rem',
        'sidebar-width': '280px',
        'container-max': '1200px',
        'page-margin': '64px',
        'column-gap': '40px',
        'row-gap': '24px'
      },
      fontFamily: {
        // code.html families
        'label-xs': ['Inter', 'system-ui', 'sans-serif'],
        'headline-lg': ['"Playfair Display"', 'Georgia', 'serif'],
        'headline-display': ['"Playfair Display"', 'Georgia', 'serif'],
        'body-md': ['"Source Serif 4"', 'Georgia', 'serif'],
        // remit families (back-compat)
        'display-lg': ['"Playfair Display"', 'Georgia', 'serif'],
        'display-lg-mobile': ['"Playfair Display"', 'Georgia', 'serif'],
        'headline-md': ['"Playfair Display"', 'Georgia', 'serif'],
        'headline-sm': ['"Playfair Display"', 'Georgia', 'serif'],
        'label-caps': ['Inter', 'system-ui', 'sans-serif'],
        'code-ui': ['"JetBrains Mono"', 'ui-monospace', 'monospace'],
        'body-lg': ['"Source Serif 4"', 'Georgia', 'serif']
      },
      fontSize: {
        // code.html scale
        'label-xs': ['11px', { lineHeight: '14px', letterSpacing: '0.08em', fontWeight: '600' }],
        'headline-lg': ['32px', { lineHeight: '40px', fontWeight: '700' }],
        'headline-display': ['56px', { lineHeight: '64px', fontWeight: '700' }],
        'body-md': ['17px', { lineHeight: '28px', fontWeight: '400' }],
        // remit scale (back-compat)
        'display-lg': ['52px', { lineHeight: '1.05', letterSpacing: '-0.02em', fontWeight: '800' }],
        'display-lg-mobile': ['34px', { lineHeight: '1.05', fontWeight: '800' }],
        'headline-md': ['30px', { lineHeight: '1.2', fontWeight: '700' }],
        'headline-sm': ['23px', { lineHeight: '1.3', fontWeight: '700' }],
        'label-caps': ['11px', { lineHeight: '1', letterSpacing: '0.1em', fontWeight: '700' }],
        'code-ui': ['14px', { lineHeight: '1.4', fontWeight: '400' }],
        'body-lg': ['19px', { lineHeight: '1.7', fontWeight: '400' }]
      },
      boxShadow: {
        brutal: 'none',
        'brutal-hover': 'none'
      }
    }
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/container-queries')
  ]
};
