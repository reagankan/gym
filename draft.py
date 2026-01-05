
def dump_exercise_names(notes_parsed, filename="raw_exercise_names.csv"):
    # with open(filename, "w", encoding="utf-8") as f:
        for note in notes_parsed:
            if not note:
                continue
            date = note[0]
            exercises = []
            for block in note[1:]:
                if isinstance(block, list) and block:
                    # skip "done." blocks if you want
                    if block[0].strip().lower() == "done.":
                        continue
                    exercises.append(block[0].strip())
            # construct line
            line = ",".join([date] + exercises)
            # f.write(line + "\n")
            print(line)
