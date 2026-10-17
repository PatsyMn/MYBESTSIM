from pathlib import Path


def build_html(stats):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>eSIM dashboard</title>
</head>
<body>
<h1>eSIM dashboard</h1>
<p>Total eSIM cards: {stats["total"]}</p>
</body>
</html>"""


def write_dashboard(stats, output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(build_html(stats), encoding="utf-8")
    return output_path


if __name__ == "__main__":
    from read_data import load_all
    from stats import compute_stats
    esims = load_all('dataset')
    path = write_dashboard(compute_stats(esims), 'output/dashboard.html')
    print("Dashboard written to", path)
