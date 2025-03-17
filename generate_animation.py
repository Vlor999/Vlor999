import json
import math

# Charger les contributions
with open("contributions.json") as f:
    data = json.load(f)

# Extraire les contributions
weeks = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
cells_map = {}
all_cells = []
max_contributions = 0
max_x = 0
max_y = 0

# Créer une grille de cellules
for i, week in enumerate(weeks):
    if i > max_x:
        max_x = i
    for j, day in enumerate(week["contributionDays"]):
        if j > max_y:
            max_y = j
        count = day["contributionCount"]
        if count > max_contributions:
            max_contributions = count
        cell = {
            "x": i,
            "y": j,
            "count": count,
            "date": day["date"],
            "original_count": count,
            "is_original": count > 0
        }
        cells_map[(i, j)] = cell
        all_cells.append(cell)

# Trier les cellules par nombre de contributions pour l'animation
cells_by_count = sorted(all_cells, key=lambda c: c["count"])

# Paramètres améliorés
SVG_WIDTH, SVG_HEIGHT = 890, 128
CELL_SIZE = 10
CELL_SPACING = 3
BORDER_RADIUS = 2
ANIMATION_DURATION = 15  # secondes pour l'animation complète
PULSE_DURATION = 1.5  # secondes pour chaque pulsation

# Palette de couleurs GitHub
GITHUB_COLORS = [
    "#ebedf0",  # 0 contributions
    "#9be9a8",  # 1-3 contributions
    "#40c463",  # 4-7 contributions
    "#30a14e",  # 8-12 contributions
    "#216e39"   # 13+ contributions
]

# Version dark mode
GITHUB_COLORS_DARK = [
    "#161b22",  # 0 contributions
    "#0e4429",  # 1-3 contributions
    "#006d32",  # 4-7 contributions
    "#26a641",  # 8-12 contributions
    "#39d353"   # 13+ contributions
]

# Fonction pour déterminer la couleur basée sur le nombre de contributions
def get_color_level(count):
    if count == 0:
        return 0
    elif count <= 3:
        return 1
    elif count <= 7:
        return 2
    elif count <= 12:
        return 3
    else:
        return 4

# Début du SVG avec style amélioré
svg = f'''
<svg width="{SVG_WIDTH}" height="{SVG_HEIGHT}" viewBox="0 0 {SVG_WIDTH} {SVG_HEIGHT}" 
     xmlns="http://www.w3.org/2000/svg">
  <style>
    @media (prefers-color-scheme: light) {{
      .background {{ fill: #ffffff; }}
      .contribution-0 {{ fill: {GITHUB_COLORS[0]}; }}
      .contribution-1 {{ fill: {GITHUB_COLORS[1]}; }}
      .contribution-2 {{ fill: {GITHUB_COLORS[2]}; }}
      .contribution-3 {{ fill: {GITHUB_COLORS[3]}; }}
      .contribution-4 {{ fill: {GITHUB_COLORS[4]}; }}
      .contribution-text {{ fill: #24292f; }}
    }}
    @media (prefers-color-scheme: dark) {{
      .background {{ fill: #0d1117; }}
      .contribution-0 {{ fill: {GITHUB_COLORS_DARK[0]}; }}
      .contribution-1 {{ fill: {GITHUB_COLORS_DARK[1]}; }}
      .contribution-2 {{ fill: {GITHUB_COLORS_DARK[2]}; }}
      .contribution-3 {{ fill: {GITHUB_COLORS_DARK[3]}; }}
      .contribution-4 {{ fill: {GITHUB_COLORS_DARK[4]}; }}
      .contribution-text {{ fill: #8b949e; }}
    }}
    .cell {{
      transition: transform 0.3s ease;
    }}
    .cell:hover {{
      transform: scale(1.2);
    }}
  </style>
  <rect width="100%" height="100%" class="background" rx="6" ry="6"/>
  
  <!-- Définition des animations -->
  <defs>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="2" result="blur"/>
      <feComposite in="SourceGraphic" in2="blur" operator="over"/>
    </filter>
'''

# Ajouter des animations réutilisables
for i in range(5):  # Pour chaque niveau de contribution
    svg += f'''
    <animate id="pulse-{i}" attributeName="opacity" 
      values="0.6;1;0.6" dur="{PULSE_DURATION}s" repeatCount="indefinite"/>
    <animate id="scale-{i}" attributeName="transform" type="scale"
      values="1;1.15;1" dur="{PULSE_DURATION}s" repeatCount="indefinite"
      additive="sum"/>
  '''

svg += '''
  </defs>
  
  <!-- Groupe pour l'animation de vague -->
  <g id="wave-container">
'''

# Créer les cellules de base avec animation en vague
for cell in all_cells:
    x_pos = cell["x"] * (CELL_SIZE + CELL_SPACING) + 40
    y_pos = cell["y"] * (CELL_SIZE + CELL_SPACING) + 10
    color_level = get_color_level(cell["count"])
    
    # Calculer le délai basé sur la distance depuis le coin supérieur gauche
    # Cela crée un effet de vague à travers le graphique
    distance = math.sqrt(cell["x"]**2 + cell["y"]**2)
    delay_factor = distance / (max_x + max_y) * 2  # Normaliser entre 0 et 2
    
    # Ajouter une séquence d'animations pour chaque cellule
    svg += f'''
  <g class="cell" data-date="{cell["date"]}" data-count="{cell["count"]}">
    <rect id="cell-{cell["x"]}-{cell["y"]}" 
          x="{x_pos}" y="{y_pos}" 
          width="{CELL_SIZE}" height="{CELL_SIZE}"
          rx="{BORDER_RADIUS}" ry="{BORDER_RADIUS}" 
          class="contribution-{color_level}">
      <animate attributeName="opacity" 
               values="0;1;1" 
               keyTimes="0;0.2;1"
               dur="{ANIMATION_DURATION}s" 
               begin="{delay_factor}s"
               repeatCount="indefinite"/>
      <animate attributeName="transform" type="scale"
               values="0;1.2;1" 
               keyTimes="0;0.15;0.3"
               dur="{ANIMATION_DURATION}s" 
               begin="{delay_factor}s"
               repeatCount="indefinite"
               additive="sum"/>
    </rect>
  </g>
'''

# Pour les cellules avec des contributions, ajouter un effet de pulsation
for cell in all_cells:
    if cell["count"] > 0:
        x_pos = cell["x"] * (CELL_SIZE + CELL_SPACING) + 40
        y_pos = cell["y"] * (CELL_SIZE + CELL_SPACING) + 10
        color_level = get_color_level(cell["count"])
        
        # Calculer un décalage pour la pulsation basé sur le nombre de contributions
        pulse_delay = cell["count"] % 5 * 0.1
        
        svg += f'''
  <circle id="pulse-{cell["x"]}-{cell["y"]}" 
          cx="{x_pos + CELL_SIZE/2}" cy="{y_pos + CELL_SIZE/2}" r="{CELL_SIZE/1.5}"
          class="contribution-{color_level}" opacity="0">
    <animate attributeName="opacity" 
             values="0;0.7;0" 
             dur="{PULSE_DURATION * 3}s" 
             begin="{ANIMATION_DURATION * 0.2 + pulse_delay}s"
             repeatCount="indefinite"/>
    <animate attributeName="r" 
             values="{CELL_SIZE/2};{CELL_SIZE*1.5};{CELL_SIZE*2.5}" 
             dur="{PULSE_DURATION * 3}s" 
             begin="{ANIMATION_DURATION * 0.2 + pulse_delay}s"
             repeatCount="indefinite"/>
  </circle>
'''

svg += '''
  </g>
'''

# Ajouter les jours de la semaine sur le côté
days = ["Dim", "Lun", "Mar", "Mer", "Jeu", "Ven", "Sam"]
for i, day in enumerate(days):
    if i <= max_y:
        svg += f'''
  <text x="10" y="{i * (CELL_SIZE + CELL_SPACING) + 19}" 
        font-family="Arial" font-size="9" class="contribution-text">{day}</text>
'''

# Ajouter des mois en haut
months = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin", "Juil", "Août", "Sept", "Oct", "Nov", "Déc"]
month_positions = [0, 4, 8, 13, 17, 21, 26, 30, 34, 39, 43, 47]
for i, month in enumerate(months):
    if i < len(month_positions) and month_positions[i] <= max_x:
        x_pos = month_positions[i] * (CELL_SIZE + CELL_SPACING) + 40
        svg += f'''
  <text x="{x_pos}" y="8" 
        font-family="Arial" font-size="9" class="contribution-text">{month}</text>
'''

# Ajouter légende en bas
legend_x = SVG_WIDTH - 250
legend_y = SVG_HEIGHT - 25
svg += f'''
  <g transform="translate({legend_x}, {legend_y})">
    <text font-family="Arial" font-size="9" class="contribution-text">Moins</text>
'''

for i in range(5):
    svg += f'''
    <rect x="{30 + i * 15}" y="-10" width="{CELL_SIZE}" height="{CELL_SIZE}" 
          rx="{BORDER_RADIUS}" ry="{BORDER_RADIUS}" class="contribution-{i}"/>
'''

svg += f'''
    <text x="{30 + 5 * 15 + 5}" y="0" font-family="Arial" font-size="9" class="contribution-text">Plus</text>
  </g>
'''

# Ajouter un titre animé
svg += f'''
  <text x="50%" y="95%" 
        text-anchor="middle" font-family="Arial" font-weight="bold" font-size="11" 
        class="contribution-text">
    Contribution Activity
    <animate attributeName="opacity" values="0.7;1;0.7" dur="3s" repeatCount="indefinite"/>
  </text>
'''

svg += "</svg>"

with open("contribution_animation.svg", "w") as f:
    f.write(svg)

print("✅ SVG animé généré avec effets originaux et répétition automatique !")