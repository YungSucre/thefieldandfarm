import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

const site = 'https://thefieldandfarm.com';

export default defineConfig({
  site,
  output: 'static',
  integrations: [sitemap()],
  markdown: {
    shikiConfig: { theme: 'github-light' },
  },
});
