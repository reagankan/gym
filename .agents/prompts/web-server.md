# Current State of the World

This python repo has a basic README.md. This should always be kept up-to-date w.r.t. the steps to setup the minimal virtual environment, minimal set of requirements.txt to pip install, minimal usage examples for each main.py CLI arg.

The main.py has two main CLI args. `--update-cache` and `--process-cache`. Update cache loads data from a local macbook Notes app into a local JSON file and `--process-cache` reads the latest JSON file and generates plots.

# Wishlist

I want to setup a free server that I can hit from the internet that will hit those two CLI args, basically each CLI arg becomes an API. The use case is I want two buttons on my phone for when I'm at the gym, I can just click and it'll update the graphs.

1. Simple pythonic webserver that can run locally on my macbook
2. It should be written in a portable way so we can deploy it to an actual free ec2 server or oracle server. (Orchestrator and retriever should do some thinking on the most future proof way in case we need to migrate compute).
3. The UI should have two options: view graphs (with a drop down of the exercises that we have plots for) and an update graph button.

Why do I choose to have an explicit update graph button instead of periodic refreshes? Because I only update my gym data when I go to the gym. It's not too regular. And sometimes I want to see my progress live on the fly while at the gym. A one click solution would be great.
