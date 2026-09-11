import tempfile
import subprocess
import json
import os

from git import Repo
import pandas as pd
import matplotlib.pyplot as plt

plt.style.use("scripts/scipy.mplstyle")

columns = ["Version", "Python", "C", "C++", "Fortran 77", "Cython"]
sloc_data = pd.DataFrame(columns=columns)

versions = [f"1.{i}.x" for i in range(19)] + ["2.0.x"]

with tempfile.TemporaryDirectory() as tmpdirname:
    print(f"Cloning into temporary directory: {tmpdirname}")
    repo = Repo.clone_from("https://github.com/scipy/scipy", tmpdirname)

    for i, version in enumerate(versions):
        print(f"Checking out version: {version}")
        branch = f"maintenance/{version}"
        # XXX: remove this once 2.0.x is released
        if branch == "maintenance/2.0.x":
            branch = "main"

        repo.git.clean("-ffdx")
        if branch == "maintenance/1.17.x":
            subprocess.run(["rm", "-rf", "scipy/sparse/linalg/_propack/PROPACK"],
                           cwd=tmpdirname)

        repo.git.checkout(branch)
        repo.git.clean("-ffdx")
        repo.git.submodule("update", "--init", "--recursive")
        if os.path.exists(os.path.join(tmpdirname, "subprojects")):
            dirs = ["scipy", "subprojects"]
        else:
            dirs = ["scipy"]
        data = subprocess.run(
            ["tokei"] + dirs + ["-o", "json"],
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
            json_data.get("FORTRAN Legacy", {}).get("code", 0),
            json_data.get("Cython", {}).get("code", 0),
        ]

fig, ax = plt.subplots(figsize=(5, 3), layout="constrained")
for language in columns[1:]:
    ax.semilogy(range(len(sloc_data["Version"])), sloc_data[language], label=language)
ax.set_xlabel("SciPy Version")
ax.set_ylabel("SLOC")
ax.set_xticks(range(len(sloc_data["Version"])))
ax.set_xticklabels(s.rstrip(".x") for s in sloc_data["Version"])
fig.legend(ncols=5, loc="outside lower center")
plt.xticks(rotation=45)
plt.show()
