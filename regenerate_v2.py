"""
Regenerate the 164 remaining emails in a more human, casual style.
Avoid AI tells: no em-dashes, no markdown, no PS, no meta-commentary,
short signature, varied templates per segment.
"""

import csv
import re
import random
from datetime import date

random.seed(0)

# Read already-drafted leads from tracker (the 15 done today, do not regenerate them)
already_done = set()
with open("envois-tracker.csv", encoding="utf-8") as f:
    reader = csv.reader(f); next(reader)
    for row in reader:
        already_done.add(row[2].lower().strip())  # email

print(f"Skipping {len(already_done)} already-drafted leads")

# Read source CSV
with open("gmass-yamm-import.csv", encoding="utf-8") as f:
    rows = list(csv.reader(f))
header = rows[0]
data = rows[1:]

# --- Templates ---

INTROS = [
    "On est Robin et Ludivine, on a un yacht qu'on privatise à la journée au départ de Carnon.",
    "Je m'appelle Robin, avec ma compagne Ludivine on a un yacht à Carnon qu'on privatise à la journée.",
    "Robin et Ludivine, on est basés à Carnon où on privatise un yacht à la journée.",
]

# Context paragraphs by segment (rotated)
CONTEXTS = {
    "A": [
        "Je vous écris parce qu'on bosse pas mal avec des structures qui veulent offrir une expérience un peu différente à leurs clients premium. Format intime, jusqu'à 10 personnes, on s'occupe de tout.",
        "On a beaucoup de demandes d'entreprises qui veulent marquer un coup avec leurs meilleurs clients. Une sortie en mer en petit comité, ça laisse une trace.",
        "Je me dis que ça peut vous parler : un yacht en privatif pour des clients que vous voulez soigner, on gère la logistique de A à Z.",
    ],
    "B": [
        "Je vous écris parce qu'on fait souvent sortir des équipes qui veulent souffler un peu après une grosse période, ou marquer un coup.",
        "L'idée : un cadre différent pour fêter une fin d'année, souder l'équipe ou récompenser une belle saison. Jusqu'à 10 personnes, on s'occupe de tout.",
        "On a pas mal d'équipes qui viennent pour sortir du quotidien le temps d'une journée. Séminaire, cohésion ou juste profiter.",
    ],
    "C": [
        "Je vous écris parce qu'on cherche à monter des collabs avec quelques {acteurs} de la région. L'idée : quand vous avez un client qui cherche un format intime hors lieu habituel, on peut faire ensemble. Commission ou co-presta, on voit.",
        "On travaille déjà avec quelques {acteurs} du coin. Le yacht en complément de votre prestation, ça ouvre pas mal de possibilités.",
        "On essaie de monter un petit réseau de partenaires sur le coin. Si vos clients cherchent parfois un format mer, on peut bosser ensemble.",
    ],
    "D": [
        "Je vous écris parce qu'on commence à monter une formule \"sortie en mer + dégustation au domaine\" avec quelques vignerons du coin. L'idée : les visiteurs qui viennent voir un domaine apprécient souvent un truc en plus sur leur journée, surtout quand ils viennent de loin.",
        "On propose à quelques domaines une combinaison yacht + dégustation pour leurs visiteurs étrangers ou clients qu'ils veulent soigner.",
        "Une idée qu'on développe : associer une sortie en mer à une visite de domaine. Format un peu différent pour vos importateurs ou visiteurs fidèles.",
    ],
    "E": [
        "Je vous écris parce qu'on fait sortir des équipes ou des clients de cabinets / d'agences de temps en temps. Format intime, jusqu'à 10 personnes, on gère tout.",
        "On a pas mal d'équipes ou de clients de structures comme la vôtre qui font des sorties ponctuelles. Séminaire, événement client, anniv de boîte, ce genre de choses.",
        "Je me dis que ça peut faire un beau cadre pour souder votre équipe ou recevoir un client important. Jusqu'à 10 personnes, on s'occupe de tout.",
    ],
}

CTAS = [
    "Pas sûr que ça vous parle, mais si oui dites-moi un mot, je vous explique comment ça se passe.",
    "Si ça vous parle, dites-moi, je vous envoie ce qu'on propose.",
    "Si vous voulez en savoir plus, dites-moi simplement, on en parle.",
    "Pas certain que ça soit pour vous, mais si oui un petit mot et je vous explique.",
]

SIGNOFFS = [
    "Bonne journée,\nRobin",
    "Belle journée,\nRobin",
    "Très belle journée à vous,\nRobin",
    "Bonne semaine,\nRobin",
]

SUBJECTS = {
    "A": [
        "Une idée pour vos clients premium",
        "Un cadre privé pour {entreprise}",
        "Une expérience à proposer à vos clients",
        "Yacht à Carnon, juste pour vous en parler",
        "Une idée à vous soumettre",
    ],
    "B": [
        "Une journée d'équipe un peu différente",
        "Yacht à Carnon, une idée séminaire",
        "Pour souder l'équipe ou souffler un coup",
        "Un cadre pour récompenser votre équipe",
        "Une journée hors les murs ?",
    ],
    "C": [
        "Une collaboration possible ?",
        "Yacht + votre prestation, ça matche ?",
        "Une carte yacht à ajouter à votre offre",
        "Bosser ensemble ?",
        "Un partenariat à étudier",
    ],
    "D": [
        "Yacht + dégustation pour vos visiteurs ?",
        "Une idée pour vos visiteurs domaine",
        "Combiner mer et dégustation ?",
        "Un format à imaginer ensemble",
    ],
    "E": [
        "Une idée pour votre équipe ou vos clients",
        "Yacht à Carnon - juste pour vous en parler",
        "Petit mot depuis Carnon",
        "Une proposition à vous soumettre",
        "Un cadre différent à imaginer",
    ],
}

# Determine "acteurs" word for segment C (varies by sector)
def acteur_word(secteur):
    s = (secteur or "").lower()
    if "traiteur" in s or "restauration" in s: return "traiteurs"
    if "wedding" in s: return "wedding planners"
    if "événementiel" in s or "evenementiel" in s: return "agences événementielles"
    if "hôtel" in s or "hotel" in s: return "hôtels"
    return "partenaires"

# Extract prenom from email if pattern looks like a first name
COMMON_FIRSTNAMES = set("""
clementine clementine clementinemartin amelie sebastien thierry celine
caroline christine philippe jean marie pierre alexandre nicolas
laurent stephane benoit thomas christophe matthieu remi julien
emmanuel arnaud florent guillaume olivier eric edouard alex
ali nadia samira fatima karim mohamed brahim
rudy sebastien herve charles luc marc paul david antoine
emilie eve eva claire julie sandra sandrine valerie nathalie
sophie helene catherine isabelle anne sylvie patricia
gael gaelle aline alice anna elsa lucile lucile lea
fanny manon laetitia mary martin maxime hugo louis leo tom
mathieu raphael yvan ivan iris cindy nancy pascal pierre-yves
robin ludivine lucas baptiste arthur jules clement
""".split())

def extract_prenom(email, prenom_field):
    if prenom_field and prenom_field.strip():
        return prenom_field.strip()
    local = email.split("@")[0].lower()
    # Skip generic patterns
    if local in ("contact","info","infos","hello","bienvenue","accueil",
                 "commercial","commerce","contactezmoi","reservation",
                 "secretariat","direction","cabinet","atelier","contact1",
                 "agence","domaine","mail","mailbox","montpellier",
                 "nimes","beziers","lattes","sete","lunel","mauguio"):
        return None
    # Try first segment of "prenom.nom"
    candidate = re.split(r"[.\-_]", local)[0]
    if len(candidate) < 3 or len(candidate) > 15:
        return None
    if candidate not in COMMON_FIRSTNAMES:
        return None
    # Capitalize properly
    return candidate.capitalize()

def make_email(row, i):
    email = row[0]
    prenom_field = row[1]
    entreprise = row[2]
    segment = row[3]
    secteur = row[4] if len(row) > 4 else ""  # not used in v2

    prenom = extract_prenom(email, prenom_field)
    salut = f"Bonjour {prenom}," if prenom else "Bonjour,"

    intro = INTROS[i % len(INTROS)]
    context_pool = CONTEXTS.get(segment, CONTEXTS["E"])
    context = context_pool[i % len(context_pool)]
    if "{acteurs}" in context:
        context = context.replace("{acteurs}", acteur_word(secteur))
    cta = CTAS[i % len(CTAS)]
    signoff = SIGNOFFS[i % len(SIGNOFFS)]

    body = f"{salut}\n\n{intro}\n\n{context}\n\n{cta}\n\n{signoff}"

    subj_pool = SUBJECTS.get(segment, SUBJECTS["E"])
    subject = subj_pool[i % len(subj_pool)].replace("{entreprise}", entreprise)

    return subject, body

# Generate
out_rows = [header]
regenerated = 0
skipped = 0
for i, row in enumerate(data):
    email = row[0].lower().strip()
    if email in already_done:
        # Keep old row as-is (for tracking completeness)
        out_rows.append(row)
        skipped += 1
        continue
    # Need to know secteur - look up from main CSV by email
    # For now use row entreprise/segment only
    # Read secteur from main file (entreprises-seminaires-montpellier.csv)
    out_row = list(row)
    subject, body = make_email(row, i)
    out_row[4] = subject  # Subject column
    out_row[5] = body     # Body column
    out_rows.append(out_row)
    regenerated += 1

# Load secteur lookup from main file to enrich Segment C templates
secteur_map = {}
with open("entreprises-seminaires-montpellier.csv", encoding="utf-8") as f:
    r = csv.reader(f); next(r)
    for row in r:
        if row[2]:
            secteur_map[row[2].lower().strip()] = row[1]

# Re-run with secteur info (for segment C)
out_rows = [header]
regenerated = 0
for i, row in enumerate(data):
    email = row[0].lower().strip()
    if email in already_done:
        out_rows.append(row)
        continue
    out_row = list(row)
    # Inject secteur into row for template
    secteur = secteur_map.get(email, "")
    row_with_secteur = list(row) + [secteur]
    subject, body = make_email(row_with_secteur, i)
    out_row[4] = subject
    out_row[5] = body
    out_rows.append(out_row)
    regenerated += 1

with open("gmass-yamm-import-v2.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
    w.writerows(out_rows)

print(f"Regenerated: {regenerated}")
print(f"Skipped (already drafted): {skipped}")
print(f"Total rows: {len(out_rows)-1}")

# Show samples
print("\n=== SAMPLE A ===")
for row in out_rows[1:]:
    if row[3] == "A" and row[0].lower().strip() not in already_done:
        print(f"To: {row[0]}\nSubject: {row[4]}\n\n{row[5]}\n")
        break
print("=== SAMPLE D ===")
for row in out_rows[1:]:
    if row[3] == "D" and row[0].lower().strip() not in already_done:
        print(f"To: {row[0]}\nSubject: {row[4]}\n\n{row[5]}\n")
        break
print("=== SAMPLE C ===")
for row in out_rows[1:]:
    if row[3] == "C" and row[0].lower().strip() not in already_done:
        print(f"To: {row[0]}\nSubject: {row[4]}\n\n{row[5]}\n")
        break
