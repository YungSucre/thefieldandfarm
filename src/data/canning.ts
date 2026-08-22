// Tableau de mise en conserve — thefieldandfarm.
// SOURCE : USDA Complete Guide to Home Canning (National Center for Home
// Food Preservation, nchfp.uga.edu) — édition officielle, données stables.
// Méthodes : WB = water bath (bain-marie), PC = pressure canner (pression).
// Temps pour pints (pt) et quarts (qt) à l'altitude de référence.
// ⚠ Les temps changent avec l'altitude : ajouter du temps au-delà de 1000 ft.

export interface CanningItem {
  id: string;
  name: string;
  method: "wb" | "pc";
  minutesPt: number;   // minutes (pints)
  minutesQt: number;   // minutes (quarts)
  pressure: number;    // PSI (PC uniquement)
  note?: string;
}

export const CANNING: CanningItem[] = [
  // --- Fruits (bain-marie) ---
  { id: "applesauce", name: "Applesauce", method: "wb", minutesPt: 15, minutesQt: 20, note: "Hot pack" },
  { id: "apple-slices", name: "Apple slices", method: "wb", minutesPt: 15, minutesQt: 20, note: "Hot pack, syrup" },
  { id: "berries", name: "Berries (whole)", method: "wb", minutesPt: 15, minutesQt: 20, note: "Hot or raw pack" },
  { id: "cherries", name: "Cherries", method: "wb", minutesPt: 15, minutesQt: 20 },
  { id: "peaches", name: "Peaches", method: "wb", minutesPt: 20, minutesQt: 25, note: "Halves or slices" },
  { id: "pears", name: "Pears", method: "wb", minutesPt: 20, minutesQt: 25 },
  { id: "plums", name: "Plums", method: "wb", minutesPt: 20, minutesQt: 25 },
  { id: "rhubarb", name: "Rhubarb", method: "wb", minutesPt: 10, minutesQt: 15, note: "Stewed" },
  { id: "grape-juice", name: "Grape juice", method: "wb", minutesPt: 10, minutesQt: 10, note: "Juice" },
  { id: "apple-juice", name: "Apple juice", method: "wb", minutesPt: 5, minutesQt: 10, note: "Juice" },
  { id: "tomato-juice", name: "Tomato juice", method: "wb", minutesPt: 35, minutesQt: 40, note: "Add lemon juice" },
  { id: "tomatoes", name: "Tomatoes (crushed)", method: "wb", minutesPt: 35, minutesQt: 45, note: "Add lemon juice/citric acid" },
  { id: "salsa", name: "Salsa", method: "wb", minutesPt: 15, minutesQt: 20, note: "Use tested recipe only" },

  // --- Pickles & condiments (bain-marie) ---
  { id: "dill-pickles", name: "Dill pickles", method: "wb", minutesPt: 10, minutesQt: 15 },
  { id: "sweet-pickles", name: "Sweet pickles", method: "wb", minutesPt: 10, minutesQt: 15 },
  { id: "relish", name: "Relish", method: "wb", minutesPt: 10, minutesQt: 10 },
  { id: "pickled-beets", name: "Pickled beets", method: "wb", minutesPt: 30, minutesQt: 35 },
  { id: "chutney", name: "Chutney", method: "wb", minutesPt: 10, minutesQt: 10 },

  // --- Légumes (pression — obligatoire) ---
  { id: "green-beans", name: "Green beans", method: "pc", minutesPt: 20, minutesQt: 25, pressure: 11, note: "Raw pack" },
  { id: "corn", name: "Corn (whole kernel)", method: "pc", minutesPt: 55, minutesQt: 85, pressure: 11, note: "Raw pack" },
  { id: "carrots", name: "Carrots", method: "pc", minutesPt: 25, minutesQt: 30, pressure: 11, note: "Raw pack" },
  { id: "peas", name: "Peas (green)", method: "pc", minutesPt: 40, minutesQt: 40, pressure: 11, note: "Raw pack" },
  { id: "potatoes", name: "Potatoes (cubed)", method: "pc", minutesPt: 35, minutesQt: 40, pressure: 11, note: "Hot pack" },
  { id: "sweet-potatoes", name: "Sweet potatoes", method: "pc", minutesPt: 65, minutesQt: 90, pressure: 11, note: "Hot pack" },
  { id: "beets", name: "Beets", method: "pc", minutesPt: 30, minutesQt: 35, pressure: 11, note: "Hot pack" },
  { id: "asparagus", name: "Asparagus", method: "pc", minutesPt: 30, minutesQt: 40, pressure: 11, note: "Raw pack" },
  { id: "squash-winter", name: "Winter squash", method: "pc", minutesPt: 55, minutesQt: 90, pressure: 11, note: "Cubed, hot pack" },
  { id: "mushrooms", name: "Mushrooms", method: "pc", minutesPt: 45, minutesQt: 45, pressure: 11, note: "Hot pack" },
  { id: "okra", name: "Okra", method: "pc", minutesPt: 25, minutesQt: 40, pressure: 11, note: "Raw pack" },

  // --- Viandes & soupes (pression) ---
  { id: "chicken", name: "Chicken (cubed)", method: "pc", minutesPt: 75, minutesQt: 90, pressure: 11, note: "Hot pack" },
  { id: "beef-stew", name: "Beef stew", method: "pc", minutesPt: 75, minutesQt: 90, pressure: 11 },
  { id: "ground-beef", name: "Ground beef", method: "pc", minutesPt: 75, minutesQt: 90, pressure: 11, note: "Hot pack" },
  { id: "pork", name: "Pork (cubed)", method: "pc", minutesPt: 75, minutesQt: 90, pressure: 11, note: "Hot pack" },
  { id: "fish", name: "Fish (strips)", method: "pc", minutesPt: 100, minutesQt: 100, pressure: 11, note: "Raw pack" },
  { id: "soup-vegetable", name: "Vegetable soup", method: "pc", minutesPt: 60, minutesQt: 75, pressure: 11, note: "With meat stock" },
  { id: "bean-soup", name: "Bean soup", method: "pc", minutesPt: 75, minutesQt: 90, pressure: 11, note: "Soaked beans" },
];

export const CANNING_SOURCE = "USDA Complete Guide to Home Canning (NCHFP, nchfp.uga.edu)";
export const CANNING_UPDATED = "2026 edition (data stable since 2015 revision)";

// Règles d'altitude (USDA) :
// Water bath : +0 min ≤1000ft, +5 min 1001-3000ft, +10 min 3001-6000ft, +15 min 6001-8000ft
// Pressure 11psi : ≤2000ft → 11psi ; 2001-4000ft → 12psi ; 4001-6000ft → 13psi ; 6001-8000ft → 14psi
export const ALTITUDE_RULES = {
  wb: [
    { min: 0, add: 0 },
    { min: 1001, add: 5 },
    { min: 3001, add: 10 },
    { min: 6001, add: 15 },
  ],
  pc: [
    { min: 0, psi: 11 },
    { min: 2001, psi: 12 },
    { min: 4001, psi: 13 },
    { min: 6001, psi: 14 },
  ],
} as const;
