### installation

```
python -m venv .venv_gym
conda deactivate

source .venv_gym/bin/activate
pip install --upgrade pip

pip install macnotesapp beautifulsoup4 matplotlib
```

### usage

`python main.py --update-cache`

```
Reads Notes app, parses workouts

Computes start_date, end_date, num_dates

Saves JSON cache only if it doesn’t already exist
```

`python main.py --process-cache`

```
Looks for cached JSON files in the current directory

Loads the file with the most dataset dates

Prints the first 5 workouts for preview
```




### web server

```
pip install flask
python server.py
```

Open `http://localhost:8080` in a browser.

- **Update Data** — fetches workouts from macOS Notes app and saves to JSON cache (macOS only)
- **Update Graphs** — regenerates all exercise plots from the latest cache
- **Dropdown** — select an exercise to view its progress chart

To change host/port:
```
HOST=127.0.0.1 PORT=5000 python server.py
```

### terminology

shoulders. shoulder press. seated shoulder press.


TODO: incline shoulder press --> incline bench.


early chest fly --> chest fly. cables.


biceps.
biceps. standing.
biceps. standing. dumbbell. {together, both}.

biceps. preacher.
biceps. preacher machine.

biceps. seated.
biceps. seated incline bench.
biceps. bench.