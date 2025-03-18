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
            "date": day["date"]
        }
        cells_map[(i, j)] = cell
        all_cells.append(cell)

# Paramètres SVG
SVG_WIDTH, SVG_HEIGHT = 890, 128
CELL_SIZE = 12
CELL_SPACING = 3
BORDER_RADIUS = 2

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
  </style>
  
  <!-- Fond -->
  <rect width="100%" height="100%" class="background" rx="6" ry="6"/>
  
  <!-- Animation globale -->
  <animate id="masterAnimation" 
           attributeName="opacity" 
           values="1;1" 
           dur="12s" 
           begin="0s"
           repeatCount="indefinite"/>
'''

# Trier les cellules par nombre de contributions pour l'animation séquentielle
contributing_cells = [cell for cell in all_cells if cell["count"] > 0]
contributing_cells.sort(key=lambda x: x["count"])

# Créer toutes les cellules de base d'abord (grille complète)
for cell in all_cells:
    x_pos = cell["x"] * (CELL_SIZE + CELL_SPACING) + 40
    y_pos = cell["y"] * (CELL_SIZE + CELL_SPACING) + 10
    
    svg += f'''
  <rect x="{x_pos}" y="{y_pos}" 
        width="{CELL_SIZE}" height="{CELL_SIZE}"
        rx="{BORDER_RADIUS}" ry="{BORDER_RADIUS}" 
        class="contribution-0"/>
'''

# Animer les cellules avec des contributions
total_cells = len(contributing_cells)
for idx, cell in enumerate(contributing_cells):
    x_pos = cell["x"] * (CELL_SIZE + CELL_SPACING) + 40
    y_pos = cell["y"] * (CELL_SIZE + CELL_SPACING) + 10
    color_level = get_color_level(cell["count"])
    
    # Animation séquentielle basée sur l'index
    delay = idx * 0.1  # Délai progressif
    
    svg += f'''
  <rect x="{x_pos}" y="{y_pos}" 
        width="{CELL_SIZE}" height="{CELL_SIZE}"
        rx="{BORDER_RADIUS}" ry="{BORDER_RADIUS}">
    <animate attributeName="fill" 
             from="url(#grad{color_level})" to="{GITHUB_COLORS[color_level]}" 
             dur="0.5s" 
             begin="{delay}s;masterAnimation.end+{delay}s"
             fill="freeze"/>
    <animate attributeName="opacity" 
             values="0;1" 
             dur="0.5s" 
             begin="{delay}s;masterAnimation.end+{delay}s"
             fill="freeze"/>
  </rect>
'''

# Ajouter des dégradés pour les effets visuels
svg += '''
  <defs>
'''

for i in range(5):
    svg += f'''
    <linearGradient id="grad{i}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{GITHUB_COLORS[i]};stop-opacity:0.8" />
      <stop offset="100%" style="stop-color:{GITHUB_COLORS[i]};stop-opacity:1" />
    </linearGradient>
'''

svg += '''
  </defs>
'''

# Ajouter un effet qui se répète après l'apparition de toutes les cellules
svg += f'''
  <rect width="100%" height="100%" fill="none" stroke="#4a9eff" stroke-width="2" rx="6" ry="6" opacity="0">
    <animate attributeName="opacity" 
             values="0;0.4;0" 
             dur="3s" 
             begin="{total_cells * 0.1 + 1}s;masterAnimation.end+{total_cells * 0.1 + 1}s" 
             repeatCount="1"/>
    <animate attributeName="stroke-width" 
             values="1;3;1" 
             dur="3s" 
             begin="{total_cells * 0.1 + 1}s;masterAnimation.end+{total_cells * 0.1 + 1}s" 
             repeatCount="1"/>
  </rect>
'''

# Fermer le SVG
svg += '</svg>'

with open("contribution_animation.svg", "w") as f:
    f.write(svg)

print("✅ SVG animé généré avec une animation séquentielle simplifiée!")