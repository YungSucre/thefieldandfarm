// Données du Soil Amendment Calculator — thefieldandfarm.
// SOURCES (taux standard des extension services universitaires) :
// - UMass Extension (soil test recommendations)
// - Oregon State University Extension (lime & sulfur rates)
// - Clemson Cooperative Extension (organic matter)
// Les taux de chaulage varient selon le type de sol (sableux/limoneux/argileux).

export interface AmendmentOption {
  id: string;
  name: string;
  unit: string;
  desc: string;
}

export const AMENDMENTS: AmendmentOption[] = [
  { id: "compost", name: "Compost (finished)", unit: "cubic feet", desc: "1-2 inches over the bed per year" },
  { id: "lime", name: "Agricultural lime (raises pH)", unit: "pounds", desc: "To raise pH one full point" },
  { id: "sulfur", name: "Elemental sulfur (lowers pH)", unit: "pounds", desc: "To lower pH one full point" },
  { id: "manure", name: "Aged manure", unit: "cubic feet", desc: "1 inch over the bed per year" },
  { id: "blood-meal", name: "Blood meal (13-0-0)", unit: "pounds", desc: "High nitrogen, quick release" },
  { id: "bone-meal", name: "Bone meal (2-14-0)", unit: "pounds", desc: "Phosphorus for roots and blooms" },
  { id: "greensand", name: "Greensand (0-0-3)", unit: "pounds", desc: "Potassium + trace minerals" },
];

// Taux par amendement (par 100 sq ft, sauf mention) :
// - compost : 1-2" = ~15-30 lb par 100 sq ft (ou volume en cu ft : 100 sq ft × 1" ≈ 8.3 cu ft)
// - lime : selon sol — sableux 5 lb, limoneux 8 lb, argileux 12 lb par 100 sq ft pour +1 pH
// - soufre : sableux 0.5 lb, limoneux 1.5 lb, argileux 2 lb par 100 sq ft pour -1 pH
// - fumier : 1" ≈ 8.3 cu ft par 100 sq ft
// - blood meal : 1-2 lb par 100 sq ft (application légère)
// - bone meal : 2-3 lb par 100 sq ft
// - greensand : 3-5 lb par 100 sq ft

export type SoilType = "sandy" | "loam" | "clay";

export const SOIL_TYPES: Record<SoilType, string> = {
  sandy: "Sandy soil",
  loam: "Loamy soil",
  clay: "Clay soil",
};

export interface RateRule {
  base: number;         // lb par 100 sq ft (ou cu ft pour les volumes)
  soilFactor: Record<SoilType, number>;
  isVolume?: boolean;   // true = résultat en cubic feet
}

export const RATES: Record<string, RateRule> = {
  compost: { base: 8.3, soilFactor: { sandy: 1, loam: 1, clay: 1 }, isVolume: true }, // 1" = 8.3 cu ft/100sqft
  lime:    { base: 8, soilFactor: { sandy: 0.6, loam: 1, clay: 1.5 } },
  sulfur:  { base: 1.5, soilFactor: { sandy: 0.33, loam: 1, clay: 1.33 } },
  manure:  { base: 8.3, soilFactor: { sandy: 1, loam: 1, clay: 1 }, isVolume: true },
  "blood-meal": { base: 1.5, soilFactor: { sandy: 1, loam: 1, clay: 1 } },
  "bone-meal":  { base: 2.5, soilFactor: { sandy: 1, loam: 1, clay: 1 } },
  greensand:    { base: 4, soilFactor: { sandy: 1, loam: 1, clay: 1 } },
};

export const AMENDMENT_SOURCE = "UMass Extension, Oregon State University Extension, Clemson Cooperative Extension";
export const AMENDMENT_UPDATED = "2026 (standard soil test recommendations)";
