import os, json, urllib.request

def fetch(user, token):
    q = '{user(login:"%s"){contributionsCollection{contributionCalendar{weeks{contributionDays{date contributionCount}}}}}}' % user
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": q}).encode(),
        headers={"Authorization": "bearer " + token, "Content-Type": "application/json", "User-Agent": "graph"},
    )
    d = json.load(urllib.request.urlopen(req))
    weeks = d["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    return [(w["contributionDays"][0]["date"], sum(x["contributionCount"] for x in w["contributionDays"])) for w in weeks]

def render(data, user):
    W, H, L, R, T, B = 800, 280, 50, 20, 60, 40
    vals = [v for _, v in data]
    top = max(max(vals), 5)
    n = len(vals)
    X = lambda i: L + i * (W - L - R) / max(n - 1, 1)
    Y = lambda v: T + (H - T - B) * (1 - v / top)
    pts = [(X(i), Y(v)) for i, v in enumerate(vals)]
    line = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    area = f"{L},{H-B} {line} {W-R},{H-B}"
    grid = "".join(
        f'<line x1="{L}" x2="{W-R}" y1="{Y(top*k/4):.1f}" y2="{Y(top*k/4):.1f}" stroke="#ffc8dd" stroke-opacity=".5"/>'
        f'<text x="{L-8}" y="{Y(top*k/4)+4:.1f}" text-anchor="end" font-size="10" fill="#7a7a9d">{round(top*k/4)}</text>'
        for k in range(5)
    )
    months, last = "", None
    names = "Jan Fev Mar Abr Mai Jun Jul Ago Set Out Nov Dez".split()
    for i, (dt, _) in enumerate(data):
        m = dt[5:7]
        if m != last:
            months += f'<text x="{X(i):.1f}" y="{H-B+18}" font-size="10" fill="#7a7a9d">{names[int(m)-1]}</text>'
            last = m
    dots = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.5" fill="#a2d2ff"/>' for (x, y), v in zip(pts, vals) if v)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Segoe UI, Arial, sans-serif">
<defs><linearGradient id="g" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#ff8fab" stop-opacity=".7"/><stop offset="1" stop-color="#ffc8dd" stop-opacity=".05"/></linearGradient></defs>
<text x="{W/2}" y="30" text-anchor="middle" font-size="18" font-weight="600" fill="#ff8fab">{user}'s Contribution Graph 🌸</text>
{grid}<polygon points="{area}" fill="url(#g)"/><polyline points="{line}" fill="none" stroke="#ff8fab" stroke-width="2.5" stroke-linejoin="round"/>{dots}{months}
</svg>'''

if __name__ == "__main__":
    user = os.environ["GH_USER"]
    data = fetch(user, os.environ["GH_TOKEN"])
    os.makedirs("dist", exist_ok=True)
    open("dist/graph.svg", "w", encoding="utf-8").write(render(data, user))
