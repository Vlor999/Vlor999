import json
import random
import math

# Charger les contributions
with open("contributions.json") as f:
    data = json.load(f)

# Extraire les contributions
weeks = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
cells = []
max_contributions = 0

for i, week in enumerate(weeks):
    for j, day in enumerate(week["contributionDays"]):
        count = day["contributionCount"]
        if count > max_contributions:
            max_contributions = count
        cells.append({
            "x": i,
            "y": j,
            "count": count,
            "date": day["date"]
        })

# Paramètres améliorés pour correspondre au style GitHub
SVG_WIDTH, SVG_HEIGHT = 890, 128
CELL_SIZE = 10
CELL_SPACING = 3
ANIMATION_DURATION = 15  # secondes pour une animation plus lente et élégante
ANIMATION_DELAY_FACTOR = 0.05
BORDER_RADIUS = 2
RIPPLE_DURATION = 3  # secondes pour l'effet de flaque d'eau
RIPPLE_MAX_SIZE = 3  # taille maximale de l'expansion

# Palette de couleurs GitHub
GITHUB_COLORS = [
    "#ebedf0",  # 0 contributions (gris très clair)
    "#9be9a8",  # 1-3 contributions (vert clair)
    "#40c463",  # 4-7 contributions (vert moyen)
    "#30a14e",  # 8-12 contributions (vert foncé)
    "#216e39"   # 13+ contributions (vert très foncé)
]

# Version dark mode
GITHUB_COLORS_DARK = [
    "#161b22",  # 0 contributions (fond sombre)
    "#0e4429",  # 1-3 contributions (vert très foncé)
    "#006d32",  # 4-7 contributions (vert foncé)
    "#26a641",  # 8-12 contributions (vert moyen)
    "#39d353"   # 13+ contributions (vert clair)
]

# Fonction pour déterminer la couleur basée sur le nombre de contributions
def get_color(count, dark_mode=True):
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
    }}
    @media (prefers-color-scheme: dark) {{
      .background {{ fill: #0d1117; }}
      .contribution-0 {{ fill: {GITHUB_COLORS_DARK[0]}; }}
      .contribution-1 {{ fill: {GITHUB_COLORS_DARK[1]}; }}
      .contribution-2 {{ fill: {GITHUB_COLORS_DARK[2]}; }}
      .contribution-3 {{ fill: {GITHUB_COLORS_DARK[3]}; }}
      .contribution-4 {{ fill: {GITHUB_COLORS_DARK[4]}; }}
    }}
    .cell {{
      transition: all 0.3s ease;
    }}
    .cell:hover {{
      transform: scale(1.1);
    }}
  </style>
  <rect width="100%" height="100%" class="background" rx="6" ry="6"/>
'''

# Créer les cellules de base
for cell in cells:
    color_level = get_color(cell["count"])
    x_pos = cell["x"] * (CELL_SIZE + CELL_SPACING) + 40  # Décalage pour laisser de la place aux labels
    y_pos = cell["y"] * (CELL_SIZE + CELL_SPACING) + 10  # Décalage pour aligner
    
    # Calcul du délai basé sur la position pour une animation de vague
    delay = (cell["x"] + cell["y"]) * ANIMATION_DELAY_FACTOR
    
    svg += f'''
  <g class="cell" data-date="{cell["date"]}" data-count="{cell["count"]}">
    <rect id="cell-{cell["x"]}-{cell["y"]}" 
          x="{x_pos}" y="{y_pos}" 
          width="{CELL_SIZE}" height="{CELL_SIZE}"
          rx="{BORDER_RADIUS}" ry="{BORDER_RADIUS}" 
          class="contribution-{color_level}">
      <animate attributeName="opacity" 
               from="0" to="1" 
               dur="0.5s" 
               begin="{delay}s" 
               fill="freeze"/>
    </rect>
'''
    
    # Ajouter l'effet de flaque d'eau uniquement pour les cellules avec contributions
    if cell["count"] > 0:
        # Plusieurs vagues pour l'effet flaque
        for i in range(1, 4):
            ripple_size = RIPPLE_MAX_SIZE * i / 3
            ripple_delay = delay + i * 0.5
            ripple_duration = RIPPLE_DURATION - i * 0.2
            
            svg += f'''
    <circle cx="{x_pos + CELL_SIZE/2}" cy="{y_pos + CELL_SIZE/2}" r="{CELL_SIZE/2}" 
            fill="none" stroke="rgba(255, 255, 255, 0.3)" stroke-width="1">
      <animate attributeName="r" 
               values="{CELL_SIZE/2};{CELL_SIZE/2 + ripple_size}" 
               dur="{ripple_duration}s" 
               begin="{ripple_delay}s" 
               repeatCount="indefinite"/>
      <animate attributeName="stroke-opacity" 
               values="0.3;0" 
               dur="{ripple_duration}s" 
               begin="{ripple_delay}s" 
               repeatCount="indefinite"/>
    </circle>
'''
    
    svg += '  </g>\n'

# Ajouter les jours de la semaine sur le côté
days = ["Dim", "Lun", "Mar", "Mer", "Jeu", "Ven", "Sam"]
for i, day in enumerate(days):
    svg += f'''
  <text x="10" y="{i * (CELL_SIZE + CELL_SPACING) + 19}" 
        font-family="Arial" font-size="9" fill="#7a7a7a">{day}</text>
'''

# Ajouter des mois en haut
months = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin", "Juil", "Août", "Sept", "Oct", "Nov", "Déc"]
month_positions = [0, 4, 8, 13, 17, 21, 26, 30, 34, 39, 43, 47]
for i, month in enumerate(months):
    if i < len(month_positions):
        x_pos = month_positions[i] * (CELL_SIZE + CELL_SPACING) + 40
        svg += f'''
  <text x="{x_pos}" y="8" 
        font-family="Arial" font-size="9" fill="#7a7a7a">{month}</text>
'''

# Ajouter légende en bas
legend_x = SVG_WIDTH - 250
legend_y = SVG_HEIGHT - 25
svg += f'''
  <g transform="translate({legend_x}, {legend_y})">
    <text font-family="Arial" font-size="9" fill="#7a7a7a">Moins</text>
'''

for i in range(5):
    svg += f'''
    <rect x="{30 + i * 15}" y="-10" width="{CELL_SIZE}" height="{CELL_SIZE}" 
          rx="{BORDER_RADIUS}" ry="{BORDER_RADIUS}" class="contribution-{i}"/>
'''

svg += f'''
    <text x="{30 + 5 * 15 + 5}" y="0" font-family="Arial" font-size="9" fill="#7a7a7a">Plus</text>
  </g>
'''

svg += "</svg>"

with open("contribution_animation.svg", "w") as f:
    f.write(svg)

print("✅ SVG animé généré avec effet de flaque d'eau !")