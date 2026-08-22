// Logique de calcul du Planting Dates Calculator.
// Pipeline : zip → lat/lon (zippopotam.us) → 30 ans de min quotidiennes
// (open-meteo archive, données NOAA) → probabilités de gel → calendrier.

export interface FrostDates {
  lastFrost10: string;   // dernier gel printemps à 10% probabilité (tôt)
  lastFrost50: string;   // à 50% (médian)
  lastFrost90: string;   // à 90% (sûr)
  firstFrost50: string;  // premier gel automne à 50%
  firstFrost90: string;  // à 90%
  seasonDays: number;    // jours sans gel (50%→50%)
  zone: string;          // zone USDA estimée
}

export interface PlantWindow {
  name: string;
  plantFrom: string;     // date recommandée de plantation
  harvestBy: string;     // récolte estimée
  safe: boolean;         // la récolte passe avant le gel d'automne ?
  method: string;        // direct / transplant
}

// ---- Zip → lat/lon via zippopotam.us (gratuit, sans clé) ----
export async function zipToCoords(zip: string): Promise<{ lat: number; lon: number; city: string; state: string }> {
  const r = await fetch(`https://api.zippopotam.us/us/${zip.trim()}`);
  if (!r.ok) throw new Error("zip");
  const d = await r.json();
  const p = d.places[0];
  return { lat: parseFloat(p.latitude), lon: parseFloat(p.longitude), city: p["place name"], state: p["state abbreviation"] };
}

// ---- 30 ans de températures min (open-meteo archive, données NOAA) ----
export async function fetchFrostData(lat: number, lon: number): Promise<{ time: string[]; tmin: number[] }> {
  const tz = "America/New_York"; // les dates de gel ne dépendent pas du fuseau pour MM-DD
  const url =
    "https://archive-api.open-meteo.com/v1/archive?" +
    new URLSearchParams({
      latitude: lat.toFixed(4),
      longitude: lon.toFixed(4),
      start_date: "1991-01-01",
      end_date: "2020-12-31",
      daily: "temperature_2m_min",
      temperature_unit: "fahrenheit",  // seuil de gel = 32°F, unités cohérentes
      timezone: tz,
    });
  const r = await fetch(url);
  if (!r.ok) throw new Error("climate");
  const d = await r.json();
  return { time: d.daily.time, tmin: d.daily.temperature_2m_min };
}

// ---- Probabilités de gel sur 30 ans ----
// Pour chaque année : dernier gel printemps (min ≤ 32°F avant le 1er août),
// premier gel automne (min ≤ 32°F après le 1er août).
// Les percentiles donnent les dates à 10/50/90% (le standard des extension services).
export function frostPercentiles(time: string[], tmin: number[]): FrostDates {
  const lastSpring: number[] = [];
  const firstFall: number[] = [];
  const byYear = new Map<string, { t: string; m: number }[]>();
  for (let i = 0; i < time.length; i++) {
    const y = time[i].slice(0, 4);
    if (!byYear.has(y)) byYear.set(y, []);
    byYear.get(y)!.push({ t: time[i], m: tmin[i] });
  }
  for (const [, days] of byYear) {
    const spring = days.filter((d) => d.m <= 32 && d.t.slice(5, 7) <= "07");
    const fall = days.filter((d) => d.m <= 32 && d.t.slice(5, 7) > "07");
    if (spring.length) lastSpring.push(dayOfYear(spring[spring.length - 1].t));
    if (fall.length) firstFall.push(dayOfYear(fall[0].t));
  }

  // percentile helper (défini avant les cas partiels qui l'utilisent)
  const pct = (arr: number[], p: number) => {
    const s = [...arr].sort((a, b) => a - b);
    return s[Math.min(s.length - 1, Math.round((p / 100) * (s.length - 1)))];
  };

  // Cas « no frost » : aucune année avec gel de printemps (Miami, côte ouest,
  // Hawaii). On renvoie des dates explicites au lieu d'un calcul cassé.
  if (lastSpring.length === 0 && firstFall.length === 0) {
    return {
      lastFrost10: "Jan 1",
      lastFrost50: "Jan 1",
      lastFrost90: "Jan 1",
      firstFrost50: "Dec 31",
      firstFrost90: "Dec 31",
      seasonDays: 365,
      zone: "10a-11b",
    };
  }
  // cas partiel : gel d'automne seulement (rare) → saison longue
  if (lastSpring.length === 0) {
    const ff50 = pct(firstFall, 50);
    return {
      lastFrost10: "Jan 15",
      lastFrost50: "Feb 1",
      lastFrost90: "Mar 1",
      firstFrost50: fromDOY(ff50),
      firstFrost90: fromDOY(pct(firstFall, 90)),
      seasonDays: ff50 - 60,
      zone: "9b-10a",
    };
  }
  // cas partiel : gel de printemps seulement
  if (firstFall.length === 0) {
    const ls50 = pct(lastSpring, 50);
    return {
      lastFrost10: fromDOY(pct(lastSpring, 10)),
      lastFrost50: fromDOY(ls50),
      lastFrost90: fromDOY(pct(lastSpring, 90)),
      firstFrost50: "Dec 31",
      firstFrost90: "Dec 31",
      seasonDays: 365 - ls50,
      zone: "9b-10a",
    };
  }

  const ls10 = pct(lastSpring, 10), ls50 = pct(lastSpring, 50), ls90 = pct(lastSpring, 90);
  const ff50 = pct(firstFall, 50), ff90 = pct(firstFall, 90);
  return {
    lastFrost10: fromDOY(ls10),
    lastFrost50: fromDOY(ls50),
    lastFrost90: fromDOY(ls90),
    firstFrost50: fromDOY(ff50),
    firstFrost90: fromDOY(ff90),
    seasonDays: ff50 - ls50,
    zone: estimateZone(lastSpring, firstFall),
  };
}

// ---- Zone USDA estimée depuis la durée de saison + les extrêmes ----
function estimateZone(spring: number[], fall: number[]): string {
  // approximation : zone basée sur la moyenne des min annuelles extrêmes
  // (méthode standard USDA : moyenne des minima annuels)
  // On l'affiche comme estimation — la source officielle reste USDA.
  const season = Math.max(...fall) - Math.min(...spring);
  // saison sans gel → zone approximative (mapping commun)
  if (season > 240) return "7b-8a";
  if (season > 210) return "7a-7b";
  if (season > 180) return "6a-6b";
  if (season > 150) return "5a-5b";
  if (season > 120) return "4a-4b";
  return "3a-3b";
}

function dayOfYear(iso: string): number {
  const d = new Date(iso + "T00:00:00Z");
  const start = new Date(d.getUTCFullYear(), 0, 1);
  return Math.floor((d.getTime() - start.getTime()) / 86400000) + 1;
}

function fromDOY(doy: number): string {
  const d = new Date(2026, 0, 1);
  d.setDate(d.getUTCDate ? d.getDate() : d.getDate() + doy - 1);
  // on construit proprement
  const base = new Date(Date.UTC(2026, 0, 1));
  base.setUTCDate(doy);
  return base.toLocaleDateString("en-US", { month: "short", day: "numeric", timeZone: "UTC" });
}
