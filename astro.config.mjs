// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

export default defineConfig({
  integrations: [
    starlight({
      title: 'MeaningWire',
      description: 'Define meaning once. Map systems at the edges.',
      customCss: ['./src/styles/meaningwire.css'],
      social: [
        {
          icon: 'github',
          label: 'MeaningWire on GitHub',
          href: 'https://github.com/MeaningWire/MeaningWire',
        },
      ],
      sidebar: [
        {
          label: 'Start',
          items: [{ label: 'Getting started', slug: 'getting-started' }],
        },
        {
          label: 'Build',
          items: [
            { label: 'Builder', slug: 'builder' },
            { label: 'Integration & evaluation', slug: 'integration-evaluation' },
          ],
        },
        {
          label: 'Understand',
          items: [{ label: 'Researcher & model', slug: 'researcher-model' }],
        },
      ],
    }),
  ],
});
