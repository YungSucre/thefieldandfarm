// Endpoint Astro : /openapi.json: documente la ressource machine-readable du site
import type { APIRoute } from "astro";
import { SITE, CATEGORIES } from "../config";

export const GET: APIRoute = () => {
  const spec = {
    openapi: "3.1.0",
    info: {
      title: SITE.name,
      description: SITE.description,
      version: "1.0.0",
    },
    servers: [{ url: SITE.url }],
    paths: {
      "/guides/{vertical}/": {
        get: {
          summary: "List guides for a practice vertical",
          parameters: [
            {
              name: "vertical",
              in: "path",
              required: true,
              schema: {
                type: "string",
                enum: CATEGORIES.flatMap((c) => c.verticals.map((v) => v.id)),
              },
            },
          ],
          responses: { "200": { description: "Hub page with guides" } },
        },
      },
      "/guides/{vertical}/{slug}/": {
        get: {
          summary: "Get a single guide",
          parameters: [
            { name: "vertical", in: "path", required: true, schema: { type: "string" } },
            { name: "slug", in: "path", required: true, schema: { type: "string" } },
          ],
          responses: { "200": { description: "Article page" } },
        },
      },
    },
  };
  return new Response(JSON.stringify(spec), {
    headers: { "Content-Type": "application/json" },
  });
};
