// Base agronomique du Planting Dates Calculator.
// Sources : University of Maryland Extension (vegetable planting calendar),
// Cornell Cooperative Extension, USDA hardiness guidance, Almanac.com.
// DTM = days to maturity ; "transplant" = DTM depuis le repiquage,
// "direct" = DTM depuis le semis direct. Valeurs standards publiées.
export interface Veggie {
  id: string;
  name: string;
  dtm: number;            // jours à maturité (standard)
  method: "transplant" | "direct" | "either";
  frost: "hardy" | "semi" | "tender";   // tolérance au gel
  minGerm: number;        // température min de germination °F
  notes?: string;
}

export const VEGGIES: Veggie[] = [
  // --- Légumes racines : semis direct, rustiques ---
  { id: "beets",        name: "Beets",            dtm: 55,  method: "direct", frost: "hardy", minGerm: 40 },
  { id: "carrots",      name: "Carrots",          dtm: 70,  method: "direct", frost: "hardy", minGerm: 40 },
  { id: "radishes",     name: "Radishes",         dtm: 25,  method: "direct", frost: "hardy", minGerm: 40 },
  { id: "turnips",      name: "Turnips",          dtm: 55,  method: "direct", frost: "hardy", minGerm: 40 },
  { id: "parsnips",     name: "Parsnips",         dtm: 120, method: "direct", frost: "hardy", minGerm: 40 },
  { id: "potatoes",     name: "Potatoes",         dtm: 90,  method: "direct", frost: "semi",  minGerm: 45 },
  { id: "sweet-potatoes", name: "Sweet Potatoes", dtm: 110, method: "transplant", frost: "tender", minGerm: 60 },
  { id: "onions",       name: "Onions (sets)",    dtm: 90,  method: "direct", frost: "hardy", minGerm: 40 },
  { id: "garlic",       name: "Garlic",           dtm: 240, method: "direct", frost: "hardy", minGerm: 35, notes: "Planted in fall, harvested the following summer." },

  // --- Feuilles : direct, rustiques ---
  { id: "lettuce",      name: "Lettuce",          dtm: 50,  method: "either", frost: "semi",  minGerm: 40 },
  { id: "spinach",      name: "Spinach",          dtm: 45,  method: "direct", frost: "hardy", minGerm: 35 },
  { id: "kale",         name: "Kale",             dtm: 55,  method: "either", frost: "hardy", minGerm: 40 },
  { id: "swiss-chard",  name: "Swiss Chard",      dtm: 55,  method: "direct", frost: "hardy", minGerm: 40 },
  { id: "arugula",      name: "Arugula",          dtm: 40,  method: "direct", frost: "hardy", minGerm: 40 },
  { id: "bok-choy",     name: "Bok Choy",         dtm: 45,  method: "either", frost: "semi",  minGerm: 45 },

  // --- Brassicacées : transplant, semi-rustiques ---
  { id: "broccoli",     name: "Broccoli",         dtm: 70,  method: "transplant", frost: "semi", minGerm: 45 },
  { id: "cabbage",      name: "Cabbage",          dtm: 70,  method: "transplant", frost: "hardy", minGerm: 40 },
  { id: "cauliflower",  name: "Cauliflower",      dtm: 70,  method: "transplant", frost: "semi", minGerm: 45 },
  { id: "brussels-sprouts", name: "Brussels Sprouts", dtm: 90, method: "transplant", frost: "hardy", minGerm: 45 },

  // --- Tomates & solanacées : transplant, tendres ---
  { id: "tomatoes",     name: "Tomatoes",         dtm: 70,  method: "transplant", frost: "tender", minGerm: 60 },
  { id: "peppers",      name: "Peppers",          dtm: 70,  method: "transplant", frost: "tender", minGerm: 65 },
  { id: "eggplant",     name: "Eggplant",         dtm: 75,  method: "transplant", frost: "tender", minGerm: 65 },

  // --- Cucurbitacées : direct (ou transplant), tendres ---
  { id: "cucumbers",    name: "Cucumbers",        dtm: 55,  method: "either", frost: "tender", minGerm: 60 },
  { id: "squash-summer", name: "Summer Squash",   dtm: 50,  method: "direct", frost: "tender", minGerm: 60 },
  { id: "squash-winter", name: "Winter Squash",   dtm: 90,  method: "direct", frost: "tender", minGerm: 60 },
  { id: "pumpkins",     name: "Pumpkins",         dtm: 100, method: "direct", frost: "tender", minGerm: 60 },
  { id: "zucchini",     name: "Zucchini",         dtm: 50,  method: "direct", frost: "tender", minGerm: 60 },
  { id: "watermelon",   name: "Watermelon",       dtm: 85,  method: "transplant", frost: "tender", minGerm: 65 },
  { id: "cantaloupe",   name: "Cantaloupe",       dtm: 80,  method: "transplant", frost: "tender", minGerm: 65 },

  // --- Légumineuses : direct, semi ---
  { id: "beans-bush",   name: "Bush Beans",       dtm: 55,  method: "direct", frost: "tender", minGerm: 60 },
  { id: "beans-pole",   name: "Pole Beans",       dtm: 65,  method: "direct", frost: "tender", minGerm: 60 },
  { id: "peas",         name: "Peas",             dtm: 60,  method: "direct", frost: "hardy", minGerm: 40 },

  // --- Maïs & céréales ---
  { id: "corn",         name: "Sweet Corn",       dtm: 75,  method: "direct", frost: "tender", minGerm: 50 },

  // --- Herbes ---
  { id: "basil",        name: "Basil",            dtm: 65,  method: "transplant", frost: "tender", minGerm: 65 },
  { id: "cilantro",     name: "Cilantro",         dtm: 50,  method: "direct", frost: "semi",  minGerm: 45 },
  { id: "dill",         name: "Dill",             dtm: 60,  method: "direct", frost: "hardy", minGerm: 45 },
  { id: "parsley",      name: "Parsley",          dtm: 75,  method: "either", frost: "hardy", minGerm: 45 },
];

// Seuil de gel par tolérance :
// tender : planté APRÈS le dernier gel (90% de probabilité passé)
// semi : peut supporter un léger gel, planté après 50%
// hardy : peut être semé avant le dernier gel (3-6 semaines avant)
export const FROST_RULES = {
  tender:  { plantAfter: 0.9 },  // après le dernier gel à 90%
  semi:    { plantAfter: 0.5 },  // après le dernier gel à 50%
  hardy:   { weeksBefore: 4 },   // 4 semaines avant le dernier gel à 50%
} as const;

// La saison de croissance : à partir du dernier gel printemps (50%),
// jusqu'au premier gel automne (50%).
// Les légumes à DTM long doivent finir avant le premier gel d'automne.
