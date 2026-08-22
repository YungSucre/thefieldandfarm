// Endpoint Astro : /robots.txt
import type { APIRoute } from "astro";
import { SITE } from "../config";

export const GET: APIRoute = () => {
  const lines = [
    "User-agent: *",
    "Allow: /",
    "",
    "Sitemap: " + SITE.url + "/sitemap-index.xml",
    "",
  ];
  return new Response(lines.join("\n"), {
    headers: { "Content-Type": "text/plain; charset=utf-8" },
  });
};
