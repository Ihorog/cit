import os, yaml
def run():
    m_file = 'cimeika_matrix.yaml'
    if not os.path.exists(m_file): return "Error: Matrix file missing"
    with open(m_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    langs, states, intents = ['en', 'uk'], data.get('states', []), data.get('intents', [])
    for l in langs:
        for s in states:
            for i in intents:
                path = f"public/{l}/{s}/{i}"
                os.makedirs(path, exist_ok=True)
                with open(f"{path}/index.html", "w", encoding="utf-8") as f:
                    f.write(f"<h1>{s} - {i} ({l})</h1>")
    return f"Success: {len(langs)*len(states)*len(intents)} nodes generated"
print(run())
