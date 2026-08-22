import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const articles = defineCollection({
  loader: glob({ pattern: '**/*.{md,mdx}', base: './src/content/articles' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    section: z.string().default('guides'),
    /** Vertical : legal, dental, vet, chiro, optometry… */
    vertical: z.string(),
    verticalName: z.string(),
    slug: z.string().regex(/^[a-z0-9]+(?:-[a-z0-9]+)*$/),
    status: z.enum(['draft', 'published']).default('draft'),
    pubDate: z.coerce.date(),
    updated: z.coerce.date().optional(),
    hero_image: z.string().optional(),
    hero_alt: z.string().optional(),
    hero_credit: z.string().optional(),
    affiliate_ready: z.boolean().default(false),
    affiliate_fit: z.array(z.string()).optional(),
  }),
});

export const collections = { articles };
