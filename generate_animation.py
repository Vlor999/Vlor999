import json
import random

# Charger les contributions
with open("contributions.json") as f:
    data = json.load(f)

# Extraire les contributions
weeks = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
cells_map = {}  # Pour accéder facilement aux cellules par coordonnées
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
            "original_count": count,  # Conserver la valeur originale
            "is_original": count > 0  # Marquer si c'est une cellule originale avec contribution
        }
        cells_map[(i, j)] = cell
        all_cells.append(cell)

# Paramètres améliorés
SVG_WIDTH, SVG_HEIGHT = 890, 128
CELL_SIZE = 10
CELL_SPACING = 3
BORDER_RADIUS = 2
ANIMATION_DELAY_FACTOR = 0.05
EXPANSION_ITERATIONS = 3  # Nombre d'itérations pour l'expansion
EXPANSION_DELAY = 2  # Délai en secondes entre chaque itération

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

# Fonction pour obtenir les cellules voisines
def get_neighbors(x, y):
    neighbors = []
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # Droite, bas, gauche, haut
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if (nx, ny) in cells_map:
            neighbors.append(cells_map[(nx, ny)])
    return neighbors

# Calculer les propagations
expansion_iterations = []
for iteration in range(EXPANSION_ITERATIONS):
    # Nouvelle liste pour cette itération
    new_propagations = []
    
    # Pour la première itération, on commence avec les cellules originales
    if iteration == 0:
        for cell in all_cells:
            if cell["is_original"]:
                # Trouver les voisins de cette cellule qui n'ont pas de contribution
                neighbors = get_neighbors(cell["x"], cell["y"])
                for neighbor in neighbors:
                    if neighbor["original_count"] == 0:  # Seulement propager vers les cellules vides
                        # Ajouter à la liste de propagation pour cette itération
                        propagation_value = max(1, cell["original_count"] // 2)  # Réduire l'intensité
                        new_propagations.append({
                            "x": neighbor["x"],
                            "y": neighbor["y"],
                            "count": propagation_value,
                            "iteration": iteration + 1
                        })
    else:
        # Pour les itérations suivantes, on utilise les cellules de l'itération précédente
        prev_iteration = expansion_iterations[iteration - 1]
        for prop in prev_iteration:
            cell_coords = (prop["x"], prop["y"])
            if cell_coords in cells_map:
                neighbors = get_neighbors(prop["x"], prop["y"])
                for neighbor in neighbors:
                    # Ne propager que vers des cellules vides et qui n'ont pas encore été propagées
                    if neighbor["original_count"] == 0 and not any(
                        p["x"] == neighbor["x"] and p["y"] == neighbor["y"] 
                        for i in range(iteration) 
                        for p in expansion_iterations[i]
                    ):
                        propagation_value = max(1, prop["count"] // 2)  # Réduire encore l'intensité
                        new_propagations.append({
                            "x": neighbor["x"],
                            "y": neighbor["y"],
                            "count": propagation_value,
                            "iteration": iteration + 1
                        })
    
    expansion_iterations.append(new_propagations)

# Début du SVG
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
    .cell-original {{
      filter: drop-shadow(0 0 2px rgba(255, 255, 255, 0.3));
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

# Créer les cellules de base d'abord (toutes avec count=0)
for cell in all_cells:
    x_pos = cell["x"] * (CELL_SIZE + CELL_SPACING) + 40
    y_pos = cell["y"] * (CELL_SIZE + CELL_SPACING) + 10
    
    # Animation initiale pour toutes les cellules
    delay = (cell["x"] + cell["y"]) * ANIMATION_DELAY_FACTOR
    
    svg += f'''
  <g class="cell" data-date="{cell["date"]}" data-count="{cell["original_count"]}">
    <rect id="cell-{cell["x"]}-{cell["y"]}" 
          x="{x_pos}" y="{y_pos}" 
          width="{CELL_SIZE}" height="{CELL_SIZE}"
          rx="{BORDER_RADIUS}" ry="{BORDER_RADIUS}" 
          class="contribution-0">
      <animate attributeName="opacity" 
               from="0" to="1" 
               dur="0.5s" 
               begin="{delay}s" 
               fill="freeze"/>
    </rect>
  </g>
'''

# Maintenant animer les cellules originales
for cell in all_cells:
    if cell["original_count"] > 0:
        x_pos = cell["x"] * (CELL_SIZE + CELL_SPACING) + 40
        y_pos = cell["y"] * (CELL_SIZE + CELL_SPACING) + 10
        color_level = get_color_level(cell["original_count"])
        delay = (cell["x"] + cell["y"]) * ANIMATION_DELAY_FACTOR + 1  # Délai après apparition initiale
        
        svg += f'''
  <rect id="original-{cell["x"]}-{cell["y"]}" 
        x="{x_pos}" y="{y_pos}" 
        width="{CELL_SIZE}" height="{CELL_SIZE}"
        rx="{BORDER_RADIUS}" ry="{BORDER_RADIUS}" 
        class="contribution-{color_level} cell-original">
    <animate attributeName="opacity" 
             from="0" to="1" 
             dur="0.5s" 
             begin="{delay}s" 
             fill="freeze"/>
  </rect>
'''

# Animer les propagations
for iteration_index, iteration_cells in enumerate(expansion_iterations):
    iteration_delay = EXPANSION_DELAY * (iteration_index + 1) + 2  # Délai après les cellules originales
    
    for prop in iteration_cells:
        x_pos = prop["x"] * (CELL_SIZE + CELL_SPACING) + 40
        y_pos = prop["y"] * (CELL_SIZE + CELL_SPACING) + 10
        color_level = get_color_level(prop["count"])
        
        # Réduire l'opacité pour chaque itération pour l'effet de dégradé
        opacity = 0.8 / (prop["iteration"])
        
        svg += f'''
  <rect id="prop-{iteration_index}-{prop["x"]}-{prop["y"]}" 
        x="{x_pos}" y="{y_pos}" 
        width="{CELL_SIZE}" height="{CELL_SIZE}"
        rx="{BORDER_RADIUS}" ry="{BORDER_RADIUS}" 
        class="contribution-{color_level}">
    <animate attributeName="opacity" 
             from="0" to="{opacity}" 
             dur="0.8s" 
             begin="{iteration_delay}s" 
             fill="freeze"/>
  </rect>
'''

# Ajouter les jours de la semaine sur le côté
days = ["Dim", "Lun", "Mar", "Mer", "Jeu", "Ven", "Sam"]
for i, day in enumerate(days):
    if i <= max_y:  # S'assurer qu'on n'ajoute que les jours nécessaires
        svg += f'''
  <text x="10" y="{i * (CELL_SIZE + CELL_SPACING) + 19}" 
        font-family="Arial" font-size="9" fill="#7a7a7a">{day}</text>
'''

# Ajouter des mois en haut
months = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin", "Juil", "Août", "Sept", "Oct", "Nov", "Déc"]
month_positions = [0, 4, 8, 13, 17, 21, 26, 30, 34, 39, 43, 47]
for i, month in enumerate(months):
    if i < len(month_positions) and month_positions[i] <= max_x:
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

print("✅ SVG animé généré avec effet de propagation des contributions !")