import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import json
import os
import re
import sys
import types
from datetime import datetime
from pathlib import Path
from flask import Flask, jsonify, Response, send_from_directory

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
#progress-container { margin: 0.5rem 0; }
progress { width: 80%; }
</style>
</head>
<body>
<h1>Gym Tracker</h1>
<div>
  <button id="btn-update" onclick="post('/api/update-cache', this)">Update Data</button>
  <button id="btn-graphs" onclick="streamGraphs()">Update Graphs</button>
</div>
<div id="status"></div>
<div id="progress-container" style="display:none;"><progress id="progress-bar" value="0" max="100"></progress> <span id="progress-text"></span></div>
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
async function streamGraphs() {
  const btn = document.getElementById('btn-graphs');
  const pc = document.getElementById('progress-container');
  const pb = document.getElementById('progress-bar');
  const pt = document.getElementById('progress-text');
  btn.disabled = true;
  pc.style.display = '';
  pb.value = 0;
  pt.textContent = '';
  status.textContent = 'Working...';
  try {
    const r = await fetch('/api/process-cache-stream', {method:'POST'});
    const reader = r.body.getReader();
    const decoder = new TextDecoder();
    let buf = '';
    while (true) {
      const {done, value} = await reader.read();
      if (done) break;
      buf += decoder.decode(value, {stream:true});
      let lines = buf.split('\\n');
      buf = lines.pop();
      for (const line of lines) {
        if (!line.startsWith('data: ')) continue;
        const d = JSON.parse(line.slice(6));
        if (d.error) { status.textContent = 'Error: ' + d.error; pc.style.display = 'none'; btn.disabled = false; return; }
        pb.max = d.total;
        pb.value = d.current;
        pt.textContent = d.current + ' / ' + d.total;
        if (d.done) {
          status.textContent = 'Generated plots for ' + d.total + ' exercises from ' + d.file;
          pc.style.display = 'none';
          btn.disabled = false;
          loadExercises();
        }
      }
    }
  } catch(e) { status.textContent = 'Error: ' + e; pc.style.display = 'none'; btn.disabled = false; }
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


@app.route("/api/process-cache-stream", methods=["POST"])
def process_cache_stream():
    def generate():
        try:
            json_files = list(Path(PROJECT_DIR).glob("workouts_start_*_end_*_num_*.json"))
            if not json_files:
                yield 'data: {"error": "No cache files found. Run Update Data first."}\n\n'
                return

            NUM_RE = re.compile(r"_num_(\d+)\.json$")
            def extract_num(p):
                m = NUM_RE.search(p.name)
                return int(m.group(1)) if m else -1

            chosen_file = max(json_files, key=extract_num)

            with open(chosen_file, "r", encoding="utf-8") as f:
                workouts = json.load(f)

            exercise_data = extract_exercise_weights(workouts)
            exercises = sorted(exercise_data.keys())
            total = len(exercises)

            for i, exercise in enumerate(exercises, 1):
                plot_exercise_boxplot(exercise, exercise_data[exercise])
                plt.close('all')
                yield f'data: {json.dumps({"current": i, "total": total, "exercise": exercise})}\n\n'

            yield f'data: {json.dumps({"current": total, "total": total, "done": True, "file": chosen_file.name})}\n\n'
        except Exception as e:
            yield f'data: {json.dumps({"error": str(e)})}\n\n'

    return Response(generate(), mimetype='text/event-stream')


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


@app.route("/api/health")
def health():
    try:
        exercises = len([f for f in os.listdir(IMGS_DIR) if f.endswith(".png")])
    except FileNotFoundError:
        exercises = 0
    return jsonify(status="ok", timestamp=datetime.utcnow().isoformat(), exercises=exercises)


if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8080"))
    app.run(host=host, port=port)
