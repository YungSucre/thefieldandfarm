"""Générateur de milliers de titres d'articles practiceownerpro.
Chaque combo (vertical × sous-niche × angle) × formats × variantes = titres uniques
qui répondent à des requêtes Google long-tail réelles.

Sortie : outputs/titles_all.jsonl (titre, slug, vertical, sub, angle, format)
"""
import json, os, re, unicodedata

ROOT = "/root/practiceownerpro"
reg = json.load(open(os.path.join(ROOT, "outputs", "vertical_register.json")))

def slugify(s):
    s = s.lower().strip()
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s

# Patrons de titres par angle (chaque patron produit 1-4 titres selon la sous-niche)
TITLE_PATTERNS = {
    "taxes": [
        "What Taxes Does a {Sub} Pay? A Complete Guide",
        "Tax Deductions for {Sub}s You Are Probably Missing",
        "How to File Quarterly Estimated Taxes as a {Sub}",
        "The {Sub} Tax Calendar: Every Deadline You Cannot Miss",
        "How Much Should a {Sub} Set Aside for Taxes?",
        "Tax Write-Offs for {Sub}s: The Complete List",
        "S-Corp vs LLC for {Sub}s: Which Saves More on Taxes?",
    ],
    "accounting": [
        "Bookkeeping for {Sub}s: A Beginner's Guide",
        "How to Do Accounting for a {Sub} Without an Accountant",
        "The Best Chart of Accounts for a {Sub}",
        "How Much Does a {Sub} Bookkeeper Cost?",
        "Cash vs Accrual Accounting for {Sub}s",
        "How to Reconcile Your {Sub} Bank Account Every Month",
    ],
    "software": [
        "Best {Sub} Software in 2026: The Complete Comparison",
        "Best Practice Management Software for {Sub}s",
        "How Much Should a {Sub} Spend on Software?",
        "Best Billing Software for {Sub}s in 2026",
        "The {Sub} Software Stack: Everything You Need",
        "Best Scheduling Software for {Sub}s",
    ],
    "hiring": [
        "How to Hire Your First Employee as a {Sub}",
        "What Does It Cost to Hire Staff in a {Sub}?",
        "The {Sub} Hiring Checklist: From Job Post to Offer",
        "How to Write a Job Description for a {Sub}",
        "Employee vs Independent Contractor for {Sub}s",
        "How to Interview Candidates for a {Sub}",
    ],
    "compliance": [
        "Compliance Checklist for {Sub}s: What You Cannot Skip",
        "The {Sub} Regulatory Requirements You Need to Know",
        "How to Stay Compliant as a {Sub} in 2026",
        "HIPAA Compliance for {Sub}s: A Practical Guide",
        "What Licenses Does a {Sub} Need?",
        "Record-Keeping Requirements for {Sub}s",
    ],
    "insurance": [
        "What Insurance Does a {Sub} Really Need?",
        "Malpractice Insurance for {Sub}s: Cost and Coverage",
        "How Much Is Insurance for a {Sub}?",
        "The {Sub} Insurance Checklist: 6 Policies to Consider",
        "Workers' Comp for {Sub}s: What You Must Know",
    ],
    "marketing": [
        "How to Market a {Sub} on a Small Budget",
        "Google Business Profile for {Sub}s: The Complete Setup",
        "The {Sub} Marketing Plan: First 90 Days",
        "How to Get Referrals as a {Sub}",
        "Local SEO for {Sub}s: A Beginner's Guide",
        "Review Management for {Sub}s: How to Get More 5-Stars",
    ],
    "startup": [
        "How to Start a {Sub}: The Complete Step-by-Step Guide",
        "The Real Cost of Starting a {Sub} in 2026",
        "How to Write a Business Plan for a {Sub}",
        "The {Sub} Startup Checklist: 25 Things to Do First",
        "How Long Does It Take to Start a {Sub}?",
        "Common Mistakes When Starting a {Sub}",
    ],
    "equipment": [
        "Best Equipment for a {Sub}: What to Buy and What to Skip",
        "How Much Does Equipment Cost for a {Sub}?",
        "The {Sub} Equipment Checklist for New Owners",
        "Used vs New Equipment for {Sub}s",
        "How to Finance Equipment for a {Sub}",
    ],
    "billing": [
        "How to Price Your Services as a {Sub}",
        "The {Sub} Billing Guide: Rates, Invoices, and Payments",
        "How to Handle Late Payments as a {Sub}",
        "Should You Take Insurance as a {Sub}?",
        "How to Raise Your Rates as a {Sub} Without Losing Clients",
    ],
    "payroll": [
        "Payroll for {Sub}s: A Step-by-Step Guide",
        "How to Set Up Payroll for a {Sub} in 2026",
        "Payroll Taxes for {Sub}s: What You Owe",
        "Best Payroll Services for {Sub}s",
    ],
    "legal structure": [
        "LLC vs PLLC for {Sub}s: Which Is Right?",
        "How to Choose a Legal Structure for a {Sub}",
        "What Is an S-Corp and Should a {Sub} Use One?",
        "The Legal Paperwork Every {Sub} Needs",
    ],
    "cash flow": [
        "How to Manage Cash Flow as a {Sub}",
        "The {Sub} Cash Flow Guide: Survive Your First Year",
        "How Much Working Capital Does a {Sub} Need?",
        "Why {Sub}s Run Out of Cash (and How to Prevent It)",
    ],
    "staffing": [
        "How Many Employees Does a {Sub} Need?",
        "The {Sub} Staffing Guide: Roles, Salaries, and Schedule",
        "How to Retain Staff in a {Sub}",
        "Part-Time vs Full-Time Staff for {Sub}s",
    ],
    "retirement": [
        "Retirement Plans for {Sub}s: SEP IRA vs Solo 401(k)",
        "How to Save for Retirement as a {Sub}",
        "The {Sub} Retirement Guide: Options Compared",
    ],
    "pricing": [
        "How to Set Your Prices as a {Sub}",
        "The {Sub} Pricing Strategy: What to Charge in 2026",
        "Value-Based Pricing for {Sub}s",
        "How to Handle Price Objections as a {Sub}",
    ],
}

# Titres supplémentaires par format (ne dépendent pas de l'angle)
FORMAT_TITLES = {
    "compare": [
        "Best {Sub} Tools Compared in 2026",
        "{Sub} Buyer's Guide: What to Look For",
    ],
    "list": [
        "{N} Mistakes {Sub}s Make in Their First Year",
        "{N} Things to Know Before You Start a {Sub}",
        "{N} Questions to Ask Before Buying a {Sub}",
    ],
    "checklist": [
        "The Complete {Sub} Startup Checklist",
        "The Annual {Sub} Review Checklist",
    ],
}

def generate():
    out = []
    seen = set()
    # normalisation : "How to Market a Solo Chiropractor" → "...Practice"
    PERSON_SUBS = {"solo attorney", "solo dentist", "solo chiropractor", "solo optometrist",
                   "single veterinarian", "newly licensed attorney"}
    VOWEL_START = ("optometry", "oral", "estate", "immigration", "endodontic", "orthodontic", "equine", "emergency")
    for combo in reg:
        vid = combo["vertical"]
        sub = combo["sub"]
        angle = combo["angle"]
        sub_title = sub.title()
        if sub in PERSON_SUBS:
            sub_title = f"{sub.title()} Practice" if not sub.endswith("practice") else sub.title()
        for pat in TITLE_PATTERNS.get(angle, []):
            t = pat.replace("{Sub}", sub_title)
            t = t.replace("Practice Practice", "Practice")
            # pas de "Start a Practice Buyer" (on n'achète pas pour démarrer)
            if "Buyer" in sub_title and ("Start a" in t or "Starting a" in t or "How to Start" in t):
                continue
            # a/an devant voyelle
            for w in VOWEL_START:
                t = t.replace(f" a {w.title()}", f" an {w.title()}")
            key = t.lower()
            if key in seen:
                continue
            seen.add(key)
            out.append({
                "title": t, "slug": slugify(t),
                "vertical": vid, "sub": sub, "angle": angle, "format": "guide",
            })
        for fmt, pats in FORMAT_TITLES.items():
            for pat in pats:
                t = pat.replace("{Sub}", sub_title).replace("{N}", str(7))
                t = t.replace("Practice Practice", "Practice")
                if "Buyer" in sub_title and ("Start a" in t or "Starting a" in t):
                    continue
                for w in VOWEL_START:
                    t = t.replace(f" a {w.title()}", f" an {w.title()}")
                key = t.lower()
                if key in seen:
                    continue
                seen.add(key)
                out.append({
                    "title": t, "slug": slugify(t),
                    "vertical": vid, "sub": sub, "angle": angle, "format": fmt,
                })
    return out

if __name__ == "__main__":
    titles = generate()
    out = os.path.join(ROOT, "outputs", "titles_all.jsonl")
    with open(out, "w") as f:
        for t in titles:
            f.write(json.dumps(t) + "\n")
    print(f"{len(titles)} titres uniques générés")
    # stats
    from collections import Counter
    by_v = Counter(t["vertical"] for t in titles)
    print("par verticale:", dict(by_v))
