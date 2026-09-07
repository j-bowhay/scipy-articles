import tempfile
import subprocess
import json

from git import Repo
import pandas as pd
import matplotlib.pyplot as plt

sloc_data = pd.DataFrame(columns=["Version", "Python", "C", "C++", "Fortran", "Cython"])

versions = [f"1.{i}.x" for i in range(19)]  # + ["2.0.x"]

with tempfile.TemporaryDirectory() as tmpdirname:
    print(f"Cloning into temporary directory: {tmpdirname}")
    repo = Repo.clone_from("https://github.com/scipy/scipy", tmpdirname)

    for i, version in enumerate(versions):
        print(f"Checking out version: {version}")
        branch = f"maintenance/{version}"
        repo.git.checkout(branch)
        repo.git.clean("-xdf")
        repo.git.submodule("update", "--init", "--recursive")
        data = subprocess.run(
            ["tokei", "scipy", "-o", "json"],
            cwd=tmpdirname,
            capture_output=True,
            text=True,
        )
        json_data = json.loads(data.stdout)
        sloc_data.loc[i] = [
            version,
            json_data.get("Python", {}).get("code", 0),
            json_data.get("C", {}).get("code", 0)
            + json_data.get("C Header", {}).get("code", 0),
            json_data.get("C++", {}).get("code", 0)
            + json_data.get("C++ Header", {}).get("code", 0),
            json_data.get("FORTRAN Legacy").get("code", 0),
            json_data.get("Cython", {}).get("code", 0),
        ]

fig, ax = plt.subplots(figsize=(10, 6), layout="constrained")
for language in ["Python", "C", "C++", "Fortran", "Cython"]:
    ax.plot(range(len(sloc_data["Version"])), sloc_data[language], label=language)
ax.set_xlabel("Version")
ax.set_ylabel("Lines of Code")
ax.set_xticks(range(len(sloc_data["Version"])))
ax.set_xticklabels(sloc_data["Version"])
ax.legend()
plt.xticks(rotation=45)
