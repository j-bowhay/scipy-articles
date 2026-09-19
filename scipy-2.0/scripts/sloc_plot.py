import tempfile
import subprocess
import json
import shutil
from pathlib import Path
import argparse

from git import Repo
import pandas as pd
import matplotlib.pyplot as plt

plt.style.use("scripts/scipy.mplstyle")

parser = argparse.ArgumentParser(description="Plot SLOC for SciPy versions")
parser.add_argument(
    "--all",
    action="store_true",
    help="Include all code, not just the parts SciPy maintains.",
)
args = parser.parse_args()


columns = ["Version", "Python", "C", "C++", "Fortran 77", "Cython"]
sloc_data = pd.DataFrame(columns=columns)

versions = [f"1.{i}.x" for i in range(19)] + ["2.0.x"]

with tempfile.TemporaryDirectory() as tmpdirname:
    print(f"Cloning into temporary directory: {tmpdirname}")
    repo = Repo.clone_from(
        "https://github.com/scipy/scipy",
        tmpdirname,
        multi_options=["--depth=1", "--no-single-branch"],
    )
    for i, version in enumerate(versions):
        print(f"Checking out version: {version}")
        branch = f"maintenance/{version}"
        # XXX: remove this once 2.0.x is released
        if branch == "maintenance/2.0.x":
            branch = "main"

        repo.git.clean("-ffdx")
        if branch == "maintenance/1.17.x":
            subprocess.run(
                ["rm", "-rf", "scipy/sparse/linalg/_propack/PROPACK"], cwd=tmpdirname
            )

        repo.git.checkout(branch)
        repo.git.clean("-ffdx")
        repo.git.submodule(
            "update", "--init", "--recursive", "--jobs", "8", "--depth", "1"
        )
        if args.all:
            # At one point SciPy wrapped the entire Boost library when we really only used
            # Boost.Math so we don't count the rest of Boost in our SLOC numbers.
            boost_dir = Path(tmpdirname) / "scipy" / "_lib" / "boost" / "boost"
            if boost_dir.exists():
                for path in boost_dir.iterdir():
                    if path.name != "math":
                        if path.is_dir():
                            shutil.rmtree(path)
                        else:
                            path.unlink()

            if (Path(tmpdirname) / "subprojects").exists():
                dirs = ["scipy", "subprojects"]
            else:
                dirs = ["scipy"]
        else:
            # remove code from https://github.com/scipy/scipy/issues/21232 except the
            # parts that are inactive upstream
            boost_dir = Path(tmpdirname) / "scipy" / "_lib" / "boost"
            if boost_dir.exists():
                shutil.rmtree(boost_dir)
            boost_math_dir = Path(tmpdirname) / "scipy" / "_lib" / "boost_math"
            if boost_math_dir.exists():
                shutil.rmtree(boost_math_dir)

            qhull_dir = Path(tmpdirname) / "scipy" / "spatial" / "qhull_src"
            if qhull_dir.exists():
                shutil.rmtree(qhull_dir)
            # old location
            qhull_dir = Path(tmpdirname) / "scipy" / "spatial" / "qhull"
            if qhull_dir.exists():
                shutil.rmtree(qhull_dir)

            pocketfft_dir = Path(tmpdirname) / "scipy" / "fft" / "_pocketfft"
            if pocketfft_dir.exists():
                shutil.rmtree(pocketfft_dir)
            duccfft_dir = Path(tmpdirname) / "scipy" / "fft" / "_duccfft"
            if duccfft_dir.exists():
                shutil.rmtree(duccfft_dir)

            pyprima_dir = Path(tmpdirname) / "scipy" / "_lib" / "pyprima"
            if pyprima_dir.exists():
                shutil.rmtree(pyprima_dir)

            _pep440 = Path(tmpdirname) / "scipy" / "_lib" / "_pep440.py"
            if _pep440.exists():
                _pep440.unlink()
            array_api_compat_dir = (
                Path(tmpdirname) / "scipy" / "_lib" / "array_api_compat"
            )
            if array_api_compat_dir.exists():
                shutil.rmtree(array_api_compat_dir)
            array_api_extra_dir = (
                Path(tmpdirname) / "scipy" / "_lib" / "array_api_extra"
            )
            if array_api_extra_dir.exists():
                shutil.rmtree(array_api_extra_dir)

            cobyqa_dir = Path(tmpdirname) / "scipy" / "_lib" / "cobyqa"
            if cobyqa_dir.exists():
                shutil.rmtree(cobyqa_dir)

            highs_dir = Path(tmpdirname) / "scipy" / "optimize" / "_highs"
            if highs_dir.exists():
                shutil.rmtree(highs_dir)
            highs_dir = Path(tmpdirname) / "scipy" / "_lib" / "highs"
            if highs_dir.exists():
                shutil.rmtree(highs_dir)

            unuran_dir = Path(tmpdirname) / "scipy" / "_lib" / "unuran"
            if unuran_dir.exists():
                shutil.rmtree(unuran_dir)

            direct_dir = Path(tmpdirname) / "scipy" / "optimize" / "_direct"
            if direct_dir.exists():
                shutil.rmtree(direct_dir)

            superlu_dir = (
                Path(tmpdirname) / "scipy" / "sparse" / "linalg" / "_dsolve" / "SuperLU"
            )
            if superlu_dir.exists():
                shutil.rmtree(superlu_dir)
            # old location
            superlu_dir = (
                Path(tmpdirname) / "scipy" / "sparse" / "linalg" / "dsolve" / "SuperLU"
            )
            if superlu_dir.exists():
                shutil.rmtree(superlu_dir)

            trlib_dir = Path(tmpdirname) / "scipy" / "optimize" / "_trlib"
            if trlib_dir.exists():
                shutil.rmtree(trlib_dir)

            uarray_dir = Path(tmpdirname) / "scipy" / "_lib" / "_uarray"
            if uarray_dir.exists():
                shutil.rmtree(uarray_dir)

            tempita_dir = Path(tmpdirname) / "scipy" / "_build_utils" / "tempita"
            if tempita_dir.exists():
                shutil.rmtree(tempita_dir)

            libnpyrandom_dir = Path(tmpdirname) / "scipy" / "stats" / "libnpyrandom"
            if libnpyrandom_dir.exists():
                shutil.rmtree(libnpyrandom_dir)

            docscrape = Path(tmpdirname) / "scipy" / "_lib" / "_docscrape.py"
            if docscrape.exists():
                docscrape.unlink()

            dirs = ["scipy"]
            if (Path(tmpdirname) / "subprojects" / "xsf").exists():
                # we want to include xsf since we maintain it
                dirs.append("subprojects/xsf")

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

fig, ax = plt.subplots(figsize=(4.5, 2.5), layout="constrained")
ax.stackplot(
    range(len(sloc_data["Version"])),
    sloc_data["Python"],
    sloc_data["Cython"],
    sloc_data["Fortran 77"],
    sloc_data["C"],
    sloc_data["C++"],
    labels=["Python", "Cython", "Fortran 77", "C", "C++"],
)
ax.set_xlabel("SciPy Version")
ax.set_ylabel("SLOC")
ax.set_xticks(range(len(sloc_data["Version"])))
ax.set_xlim(0, len(sloc_data["Version"]) - 1)
ax.set_xticklabels(s.rstrip(".x") for s in sloc_data["Version"])
fig.legend(ncols=5, loc="outside upper center")
plt.xticks(rotation=45)
plt.show()
