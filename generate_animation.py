import json

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

# Générer le SVG
SVG_WIDTH, SVG_HEIGHT = 800, 150
CELL_SIZE = 10
CELL_SPACING = 2
ANIMATION_DURATION = 3  # secondes

svg = f'<svg width="{SVG_WIDTH}" height="{SVG_HEIGHT}" viewBox="0 0 {SVG_WIDTH} {SVG_HEIGHT}" xmlns="http://www.w3.org/2000/svg">\n'
svg += '<rect width="100%" height="100%" fill="#ffffff" />\n'  # Fond blanc

for cell in cells:
    intensity = int((cell["count"] / max_contributions) * 255) if max_contributions > 0 else 0
    color = f"rgb({255-intensity}, {255-intensity//2}, {255})"

    delay = cell["x"] * 0.1 + cell["y"] * 0.1  # Décalage progressif de l'animation

    svg += f'''
    <rect x="{cell["x"] * (CELL_SIZE + CELL_SPACING)}" y="{cell["y"] * (CELL_SIZE + CELL_SPACING)}" width="{CELL_SIZE}" height="{CELL_SIZE}"
          fill="{color}">
        <animate attributeName="opacity" from="0" to="1" dur="{ANIMATION_DURATION}s" begin="{delay}s" fill="freeze"/>
    </rect>
    '''

svg += "</svg>"

with open("contribution_animation.svg", "w") as f:
    f.write(svg)

print("✅ SVG animé généré !")
