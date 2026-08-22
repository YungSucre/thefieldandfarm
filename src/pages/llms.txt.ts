// Endpoint Astro : /llms.txt: généré depuis la navigation (jamais obsolète)
import type { APIRoute } from "astro";
import { SITE, CATEGORIES } from "../config";

export const GET: APIRoute = () => {
  const lines: string[] = [];
  lines.push(`# ${SITE.name}`);
  lines.push("");
  lines.push(`> ${SITE.description}`);
  lines.push("");
  lines.push("The Field &amp; Farm is an independent publisher of practical business guides for practice owners: taxes, accounting, software, hiring, and compliance, organized by practice type.");
  lines.push("");
  lines.push("## Guide hubs (verticals)");
  lines.push("");
  for (const cat of CATEGORIES) {
    lines.push(`### ${cat.name}`);
    for (const v of cat.verticals) {
      lines.push(`- [${v.name}](${SITE.url}/guides/${v.id}/)`);
    }
    lines.push("");
  }
  return new Response(lines.join("\n"), {
    headers: { "Content-Type": "text/plain; charset=utf-8" },
  });
};
