"""Registre des verticals + sous-niches pour practiceownerpro.
Structure : vertical → [sous-niches] → les angles s'appliquent à chaque sous-niche.
Un article = vertical + sous-niche + angle + format.
"""
import json, os

ROOT = "/root/practiceownerpro"

VERTICALS = {
    "legal": {
        "name": "Legal Practice",
        "subs": [
            "solo attorney", "small law firm", "real estate attorney",
            "family law attorney", "immigration attorney", "criminal defense attorney",
            "personal injury attorney", "estate planning attorney", "corporate attorney",
            "newly licensed attorney",
        ],
    },
    "medical": {
        "name": "Medical Practice",
        "subs": [
            "new medical practice", "solo physician", "small medical clinic",
            "primary care practice", "pediatric practice", "dermatology practice",
            "family medicine practice", "internal medicine practice", "urgent care",
            "medical practice buyer",
        ],
    },
    "dental": {
        "name": "Dental Practice",
        "subs": [
            "new dental practice", "solo dentist", "small dental office",
            "pediatric dental practice", "orthodontic practice", "periodontal practice",
            "oral surgery practice", "endodontic practice", "dental hygiene practice",
            "dental practice buyer",
        ],
    },
    "therapy": {
        "name": "Therapy & Counseling",
        "subs": [
            "new therapy practice", "solo therapist", "small counseling practice",
            "psychology practice", "marriage and family therapy practice",
            "social work practice", "psychiatry practice", "group therapy practice",
            "online therapy practice", "therapy practice buyer",
        ],
    },
    "vet": {
        "name": "Veterinary Practice",
        "subs": [
            "new vet clinic", "small animal practice", "equine practice",
            "exotic animal practice", "mobile vet practice", "emergency vet clinic",
            "mixed practice", "specialty vet practice", "vet practice buyer",
            "single veterinarian",
        ],
    },
    "physical-therapy": {
        "name": "Physical Therapy",
        "subs": [
            "new PT practice", "solo physical therapist", "small PT clinic",
            "sports physical therapy", "orthopedic PT practice", "pediatric PT practice",
            "pelvic health practice", "PT practice buyer",
        ],
    },
    "pharmacy": {
        "name": "Pharmacy",
        "subs": [
            "new independent pharmacy", "solo pharmacist", "small pharmacy",
            "compounding pharmacy", "specialty pharmacy", "long-term care pharmacy",
            "pharmacy buyer",
        ],
    },
    "chiro": {
        "name": "Chiropractic",
        "subs": [
            "new chiropractic office", "solo chiropractor", "small chiro clinic",
            "sports chiropractic", "pediatric chiropractic", "family chiropractic",
            "chiropractic practice buyer", "cash-based practice",
        ],
    },
    "optometry": {
        "name": "Optometry",
        "subs": [
            "new optometry practice", "solo optometrist", "small optical practice",
            "independent optician", "optical retail practice", "medical optometry",
            "optometry practice buyer",
        ],
    },
    "podiatry": {
        "name": "Podiatry",
        "subs": [
            "new podiatry practice", "solo podiatrist", "small podiatry clinic",
            "sports podiatry", "diabetic foot care practice", "surgical podiatry",
            "podiatry practice buyer",
        ],
    },
    "audiology": {
        "name": "Audiology",
        "subs": [
            "new audiology practice", "solo audiologist", "small audiology clinic",
            "hearing aid practice", "pediatric audiology", "ENT practice",
            "audiology practice buyer",
        ],
    },
    "speech-therapy": {
        "name": "Speech Therapy",
        "subs": [
            "new speech therapy practice", "solo speech therapist", "small SLP practice",
            "pediatric speech therapy", "adult speech therapy", "school-based SLP practice",
            "SLP practice buyer",
        ],
    },
    "medspa": {
        "name": "Med Spa & Aesthetics",
        "subs": [
            "new med spa", "solo aesthetic provider", "small med spa",
            "injectables practice", "laser practice", "medical aesthetics clinic",
            "med spa buyer",
        ],
    },
    "accounting": {
        "name": "Accounting Firm",
        "subs": [
            "new accounting firm", "solo CPA", "small accounting practice",
            "tax practice", "bookkeeping practice", "audit firm", "accounting firm buyer",
        ],
    },
    "financial-advisory": {
        "name": "Financial Advisory",
        "subs": [
            "new advisory firm", "solo financial advisor", "small RIA",
            "wealth management practice", "fee-only advisor", "retirement planning practice",
            "advisory firm buyer",
        ],
    },
    "occupational-therapy": {
        "name": "Occupational Therapy",
        "subs": [
            "new OT practice", "solo occupational therapist", "small OT clinic",
            "pediatric OT practice", "hand therapy practice", "school-based OT practice",
            "OT practice buyer",
        ],
    },
    "acupuncture": {
        "name": "Acupuncture",
        "subs": [
            "new acupuncture practice", "solo acupuncturist", "small acupuncture clinic",
            "TCM practice", "community acupuncture", "fertility acupuncture practice",
            "acupuncture practice buyer",
        ],
    },
    "naturopathy": {
        "name": "Naturopathy",
        "subs": [
            "new naturopathic practice", "solo naturopath", "small ND clinic",
            "integrative medicine practice", "functional medicine practice",
            "naturopathic practice buyer",
        ],
    },
    "nutrition": {
        "name": "Nutrition & Dietetics",
        "subs": [
            "new nutrition practice", "solo dietitian", "small nutrition counseling practice",
            "sports nutrition practice", "pediatric nutrition practice",
            "nutrition practice buyer",
        ],
    },
    "midwifery": {
        "name": "Midwifery",
        "subs": [
            "new midwifery practice", "solo midwife", "small birth center",
            "home birth practice", "CNM practice", "midwifery practice buyer",
        ],
    },
    "nurse-practice": {
        "name": "Nurse Practitioner Practice",
        "subs": [
            "new NP practice", "solo nurse practitioner", "small NP clinic",
            "family NP practice", "psychiatric NP practice", "NP practice buyer",
        ],
    },
    "home-health": {
        "name": "Home Health",
        "subs": [
            "new home health agency", "small home care agency", "private duty agency",
            "home health franchise", "home health buyer",
        ],
    },
    "aba-therapy": {
        "name": "ABA Therapy",
        "subs": [
            "new ABA practice", "solo BCBA", "small ABA clinic",
            "pediatric ABA practice", "in-home ABA practice", "ABA practice buyer",
        ],
    },
    "functional-medicine": {
        "name": "Functional Medicine",
        "subs": [
            "new functional medicine practice", "solo FM practitioner", "small FM clinic",
            "integrative clinic", "longevity practice", "FM practice buyer",
        ],
    },
    "plastic-surgery": {
        "name": "Plastic Surgery",
        "subs": [
            "new plastic surgery practice", "solo surgeon", "small surgical practice",
            "cosmetic surgery practice", "reconstructive practice", "surgery practice buyer",
        ],
    },
    "fertility": {
        "name": "Fertility Clinic",
        "subs": [
            "new fertility clinic", "small fertility practice", "IVF clinic",
            "fertility center", "reproductive medicine practice", "fertility clinic buyer",
        ],
    },
    "architecture": {
        "name": "Architecture Firm",
        "subs": [
            "new architecture firm", "solo architect", "small architecture studio",
            "residential architecture firm", "commercial architecture firm",
            "architecture firm buyer",
        ],
    },
    "engineering": {
        "name": "Engineering Firm",
        "subs": [
            "new engineering firm", "solo engineer", "small engineering consultancy",
            "structural engineering firm", "civil engineering firm", "MEP firm",
            "engineering firm buyer",
        ],
    },
    "consulting": {
        "name": "Consulting Firm",
        "subs": [
            "new consulting firm", "solo consultant", "small consultancy",
            "management consulting firm", "IT consulting firm", "strategy consultancy",
            "consulting firm buyer",
        ],
    },
    "real-estate": {
        "name": "Real Estate Brokerage",
        "subs": [
            "new brokerage", "solo real estate agent", "small real estate brokerage",
            "property management brokerage", "commercial brokerage",
            "real estate team", "brokerage buyer",
        ],
    },
    "insurance-agency": {
        "name": "Insurance Agency",
        "subs": [
            "new insurance agency", "solo agent", "small independent agency",
            "health insurance agency", "commercial insurance agency",
            "life insurance agency", "agency buyer",
        ],
    },
    "tutoring": {
        "name": "Tutoring Center",
        "subs": [
            "new tutoring center", "solo tutor", "small tutoring business",
            "test prep center", "math tutoring center", "online tutoring business",
            "tutoring center buyer",
        ],
    },
    "music-school": {
        "name": "Music School",
        "subs": [
            "new music school", "solo music teacher", "small music studio",
            "piano studio", "guitar school", "voice studio", "music school buyer",
        ],
    },
    "martial-arts": {
        "name": "Martial Arts Studio",
        "subs": [
            "new martial arts studio", "solo instructor", "small dojo",
            "karate school", "BJJ academy", "taekwondo studio", "studio buyer",
        ],
    },
    "fitness-studio": {
        "name": "Fitness Studio",
        "subs": [
            "new fitness studio", "solo trainer", "small gym",
            "personal training studio", "group fitness studio", "Pilates studio",
            "studio buyer",
        ],
    },
    "yoga-studio": {
        "name": "Yoga Studio",
        "subs": [
            "new yoga studio", "solo instructor", "small yoga studio",
            "hot yoga studio", "online yoga business", "yoga studio buyer",
        ],
    },
    "salon": {
        "name": "Salon",
        "subs": [
            "new hair salon", "solo stylist", "small salon",
            "barbershop", "nail salon", "day spa", "salon suite", "salon buyer",
        ],
    },
}

# Angles business : chaque angle × chaque sous-niche = un cluster d'articles
ANGLES = [
    "taxes", "accounting", "software", "hiring", "compliance", "insurance",
    "marketing", "startup", "equipment", "billing", "payroll", "legal structure",
    "cash flow", "staffing", "retirement", "pricing",
]

# Formats d'articles (la pyramide)
FORMATS = {
    "guide": "how to / explainer pour débutants",
    "compare": "comparatif best X for [sous-niche]",
    "list": "X mistakes / X things to know",
    "checklist": "checklist actionnable",
}

def build_register():
    register = []
    for vid, v in VERTICALS.items():
        for sub in v["subs"]:
            for angle in ANGLES:
                register.append({
                    "vertical": vid,
                    "sub": sub,
                    "angle": angle,
                    "formats": list(FORMATS.keys()),
                })
    return register

if __name__ == "__main__":
    reg = build_register()
    out = os.path.join(ROOT, "outputs", "vertical_register.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump(reg, open(out, "w"), indent=1)
    print(f"{len(reg)} combos vertical×sous-niche×angle")
    print(f"({len(VERTICALS)} verticals, {sum(len(v['subs']) for v in VERTICALS.values())} sous-niches, {len(ANGLES)} angles)")
