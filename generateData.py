import os
import re
from pathlib import Path
import pandas as pd

# ---------- Paths ----------
BASE_DIR = Path(__file__).resolve().parent
UPLOADS_DIR = BASE_DIR / "uploads"
OUT_DIR = BASE_DIR / "generatedData"

# ---------- Helpers ----------
def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)

def emit_js_timestep_array(src_dir: Path, out_file: Path) -> None:
    """
    Find files named like '<timestep>-results.xlsx' and write:
      const timeSteps = ["timestep1", "timestep2", ...];
    """
    names = []
    for fname in os.listdir(src_dir):
        if not fname.lower().endswith((".xlsx", ".xls")):
            continue
        m = re.match(r"^([A-Za-z0-9]+)-results\.(xlsx|xls)$", fname, re.I)
        if m:
            names.append(m.group(1))

    def sort_key(s):
        m2 = re.search(r"(\d+)$", s)
        return (int(m2.group(1)) if m2 else 10**9, s)

    names = sorted(set(names), key=sort_key)

    ensure_dir(out_file.parent)
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("const timeSteps = [\n")
        for i, v in enumerate(names):
            comma = "," if i < len(names) - 1 else ""
            f.write(f'  "{v}"{comma}\n')
        f.write("];\n")
    print(f"  • Wrote {out_file.relative_to(BASE_DIR)}")

def process_excel_files(src_dir: Path, dst_dir: Path) -> None:
    ensure_dir(dst_dir)

    for fname in os.listdir(src_dir):
        if not fname.lower().endswith((".xlsx", ".xls")):
            continue

        path = src_dir / fname
        base = path.stem
        print(f"Processing {path.relative_to(BASE_DIR)} → base '{base}'")

        try:
            xl = pd.ExcelFile(path)
        except Exception as e:
            print(f"  ⚠️  Failed opening {fname}: {e}")
            continue

        # 1) spatial_{base}.csv  (from 'Nodes': node_X_pix, node_Y_pix)
        if "Nodes" in xl.sheet_names:
            nodes = xl.parse("Nodes")
            needed = [c for c in ["node_X_pix", "node_Y_pix"] if c in nodes.columns]
            if len(needed) == 2:
                spatial = nodes[needed]
                spatial_fname = dst_dir / f"spatial_{base}.csv"
                spatial.to_csv(spatial_fname, index=False)
                print(f"  • Wrote {spatial_fname.relative_to(BASE_DIR)}")
            else:
                print(f"  ⚠️  Missing columns in 'Nodes' for {fname}: {needed} found")
        else:
            print(f"  ⚠️  Sheet 'Nodes' not found in {fname}")

        # 2) edges_{base}.csv (from 'Edges')
        if "Edges" in xl.sheet_names:
            edges = xl.parse("Edges")
            cols = ["EndNodes_1", "EndNodes_2", "name",
                    "Weight", "Length", "Width", "Volume", "Type", "Distance"]
            present = [c for c in cols if c in edges.columns]
            edges_df = edges[present].copy()
            insert_at = min(3, len(edges_df.columns))
            edges_df.insert(insert_at, "edge_id", range(1, len(edges_df) + 1))
            edges_fname = dst_dir / f"edges_{base}.csv"
            edges_df.to_csv(edges_fname, index=False)
            print(f"  • Wrote {edges_fname.relative_to(BASE_DIR)}")
        else:
            print(f"  ⚠️  Sheet 'Edges' not found in {fname}")

        # 3) vertices_{base}.csv (from 'Nodes': node_Degree, node_Accessibility, node_ID)
        if "Nodes" in xl.sheet_names:
            nodes = xl.parse("Nodes")
            vcols = [c for c in ["node_Degree", "node_Accessibility", "node_ID"] if c in nodes.columns]
            if len(vcols) == 3:
                verts = nodes[vcols]
                verts_fname = dst_dir / f"vertices_{base}.csv"
                verts.to_csv(verts_fname, index=False)
                print(f"  • Wrote {verts_fname.relative_to(BASE_DIR)}")
            else:
                print(f"  ⚠️  Missing vertex columns in 'Nodes' for {fname}: {vcols} found")

def main():
    if not UPLOADS_DIR.is_dir():
        print(f"Error: source directory not found: {UPLOADS_DIR}")
        raise SystemExit(1)

    # Find species folders in uploads (e.g., absidia/neurospora/wolfiporia)
    species_dirs = sorted([p for p in UPLOADS_DIR.iterdir() if p.is_dir()])
    if not species_dirs:
        species_dirs = [UPLOADS_DIR]

    for sdir in species_dirs:
        species_name = sdir.name if sdir != UPLOADS_DIR else ""
        out_subdir = OUT_DIR / species_name if species_name else OUT_DIR
        ensure_dir(out_subdir)

        print(f"\n=== {('species: ' + species_name) if species_name else 'uploads root'} ===")
        process_excel_files(sdir, out_subdir)

        # Create timeSteps.js for this species folder based on *-results.xlsx names
        # emit_js_timestep_array(sdir, out_subdir / "timeSteps.js")

if __name__ == "__main__":
    main()
