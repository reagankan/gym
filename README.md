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