import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import json
import os
import re
import sys
import types
from pathlib import Path
from flask import Flask, jsonify, send_from_directory

# Stub macnotesapp so importing main.py doesn't fail on Linux
if 'macnotesapp' not in sys.modules:
    _stub = types.ModuleType('macnotesapp')
    class _NotAvailable:
        def __call__(self, *a, **kw):
            raise ImportError("macnotesapp is not available on this platform (macOS only)")
    _stub.NotesApp = _NotAvailable()
    sys.modules['macnotesapp'] = _stub

from config_utils import refresh_config
from main import extract_exercise_weights
from plot_utils import plot_exercise_boxplot

app = Flask(__name__)

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

os.chdir(PROJECT_DIR)
refresh_config()

IMGS_DIR = os.path.join(PROJECT_DIR, "imgs")

IS_MAC = sys.platform == "darwin"

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Gym Tracker</title>
<style>
body { font-family: sans-serif; max-width: 800px; margin: 0 auto; padding: 1rem; }
button { font-size: 1rem; padding: 0.6rem 1.2rem; margin: 0.3rem; cursor: pointer; }
button:disabled { opacity: 0.5; cursor: not-allowed; }
select { font-size: 1rem; padding: 0.4rem; width: 100%; margin: 0.5rem 0; }
#status { margin: 0.5rem 0; white-space: pre-wrap; }
img { max-width: 100%; margin-top: 0.5rem; }
</style>
</head>
<body>
<h1>Gym Tracker</h1>
<div>
  <button id="btn-update" onclick="post('/api/update-cache', this)">Update Data</button>
  <button id="btn-graphs" onclick="post('/api/process-cache', this)">Update Graphs</button>
</div>
<div id="status"></div>
<select id="exercises" onchange="showImg(this.value)">
  <option value="">-- select exercise --</option>
</select>
<div id="img-container"></div>
<script>
const isMac = {{IS_MAC}};
const status = document.getElementById('status');
if (!isMac) {
  const btn = document.getElementById('btn-update');
  btn.disabled = true;
  btn.title = 'Coming soon!';
}
async function post(url, btn) {
  btn.disabled = true;
  status.textContent = 'Working...';
  try {
    const r = await fetch(url, {method:'POST'});
    const d = await r.json();
    status.textContent = d.status || d.error || JSON.stringify(d);
    if (url.includes('process-cache')) loadExercises();
  } catch(e) { status.textContent = 'Error: ' + e; }
  finally { if (isMac || btn.id !== 'btn-update') btn.disabled = false; }
}
function showImg(name) {
  const c = document.getElementById('img-container');
  c.innerHTML = '';
  if (name) {
    const img = document.createElement('img');
    img.src = '/imgs/' + encodeURIComponent(name) + '?t=' + Date.now();
    c.appendChild(img);
  }
}
async function loadExercises() {
  const r = await fetch('/api/exercises');
  const list = await r.json();
  const sel = document.getElementById('exercises');
  const cur = sel.value;
  sel.innerHTML = '<option value="">-- select exercise --</option>';
  list.forEach(f => { const o = document.createElement('option'); o.value = f; o.textContent = f.replace('.png',''); sel.appendChild(o); });
  if (cur && list.includes(cur)) { sel.value = cur; showImg(cur); }
}
loadExercises();
</script>
</body>
</html>"""


@app.route("/")
def index():
    return HTML.replace("{{IS_MAC}}", "true" if IS_MAC else "false")


@app.route("/api/update-cache", methods=["POST"])
def update_cache():
    try:
        from main import get_workouts
        from date_utils import infer_workout_date_range
        from io_utils import save_workouts_to_json

        workouts = get_workouts()
        start_date, end_date, num_dates = infer_workout_date_range(workouts)
        save_workouts_to_json(workouts, start_date, end_date, num_dates)
        return jsonify(status=f"Cached {num_dates} workouts ({start_date} to {end_date})")
    except ImportError as e:
        return jsonify(error=f"Import error (macnotesapp not available on Linux?): {e}"), 500
    except Exception as e:
        return jsonify(error=str(e)), 500


@app.route("/api/process-cache", methods=["POST"])
def process_cache():
    try:
        json_files = list(Path(PROJECT_DIR).glob("workouts_start_*_end_*_num_*.json"))
        if not json_files:
            return jsonify(error="No cache files found. Run Update Data first."), 404

        NUM_RE = re.compile(r"_num_(\d+)\.json$")
        def extract_num(p):
            m = NUM_RE.search(p.name)
            return int(m.group(1)) if m else -1

        chosen_file = max(json_files, key=extract_num)

        with open(chosen_file, "r", encoding="utf-8") as f:
            workouts = json.load(f)

        exercise_data = extract_exercise_weights(workouts)

        for exercise in sorted(exercise_data.keys()):
            plot_exercise_boxplot(exercise, exercise_data[exercise])
            plt.close('all')

        return jsonify(status=f"Generated plots for {len(exercise_data)} exercises from {chosen_file.name}")
    except Exception as e:
        return jsonify(error=str(e)), 500


@app.route("/api/exercises")
def list_exercises():
    try:
        files = sorted(f for f in os.listdir(IMGS_DIR) if f.endswith(".png"))
    except FileNotFoundError:
        files = []
    return jsonify(files)


@app.route("/imgs/<filename>")
def serve_image(filename):
    return send_from_directory(IMGS_DIR, filename)


if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8080"))
    app.run(host=host, port=port)
