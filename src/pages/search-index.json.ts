import type { APIRoute } from "astro";
import { getCollection } from "astro:content";

export const prerender = true;

export const GET: APIRoute = async () => {
  const articles = await getCollection("articles");
  const index = articles
    .filter((a) => a.data.status === "published")
    .map((a) => ({
      title: a.data.title,
      description: a.data.description,
      vertical: a.data.verticalName || a.data.vertical,
      url: `/guides/${a.data.vertical}/${a.data.slug}/`,
    }))
    .sort((a, b) => a.title.localeCompare(b.title));

  return new Response(JSON.stringify(index), {
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": "public, max-age=3600",
    },
  });
};
