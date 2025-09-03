import os, zipfile, shutil
from pathlib import Path

def ensure_dataset(local_csv="data/gym_data.csv"):
    p = Path(local_csv)
    if p.exists():
        return local_csv
    if not (os.getenv("KAGGLE_USERNAME") and os.getenv("KAGGLE_KEY")):
        raise RuntimeError(
            "Place gym_data.csv at data/gym_data.csv or set KAGGLE_USERNAME/KAGGLE_KEY."
        )
    import kaggle
    outdir = Path("data"); outdir.mkdir(parents=True, exist_ok=True)
    kaggle.api.authenticate()
    kaggle.api.dataset_download_files(
        "valakhorasani/gym-members-exercise-dataset", path=str(outdir), unzip=True
    )

    candidates = list(outdir.glob("*.csv"))
    if not candidates:
        zips = list(outdir.glob("*.zip"))
        if zips:
            with zipfile.ZipFile(zips[0]) as zf:
                zf.extractall(outdir)
            zipfile.Path(zips[0]).close()
            zips[0].unlink(missing_ok=True)
            candidates = list(outdir.glob("*.csv"))
    if not candidates:
        raise FileNotFoundError("Could not find CSV after download.")
    shutil.copy(str(candidates[0]), local_csv)
    return local_csv

