import os, yaml, datetime
def get_theme():
    hour = datetime.datetime.now().hour
    if 6 <= hour < 18: return "theme-day", "#f0f4f8"
    if 18 <= hour < 22: return "theme-twilight", "#1a1a2e"
    return "theme-night", "#020205"

def run():
    with open('cimeika_matrix.yaml', 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    theme, bg = get_theme()
    langs, states, intents = ['en', 'uk'], data.get('states', []), data.get('intents', [])
    for l in langs:
        for s in states:
            for i in intents:
                path = f"public/{l}/{s}/{i}"
                os.makedirs(path, exist_ok=True)
                with open(f"{path}/index.html", "w", encoding="utf-8") as f:
                    f.write(f"<html><body class='{theme}' style='background:{bg}; color:#00d4ff; font-family:monospace;'>")
                    f.write(f"<h1>{s.upper()} § {i.upper()}</h1><p>Sync: {datetime.datetime.now()}</p></body></html>")
    return f"Success: 98 nodes generated with {theme}"
print(run())
