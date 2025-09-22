import os
import pandas as pd

def emit_js_timestep_array(src_dir):
    names = []
    for fname in os.listdir(src_dir):
        if not fname.lower().endswith(('.xlsx', '.xls')):
            continue
        m = re.match(r'^([A-Za-z0-9]+)-results\.(xlsx|xls)$', fname, re.I)
        if m:
            names.append(m.group(1))
    def sort_key(s):
        m = re.search(r'(\d+)$', s)
        return (int(m.group(1)) if m else 10**9, s)
    names = sorted(set(names), key=sort_key)

    print("const timeSteps = [")
    for i, v in enumerate(names):
        comma = "," if i < len(names) - 1 else ""
        print(f'  "{v}"{comma}')
    print("];")
    
    emit_js_timestep_array(src_directory)

def process_excel_files(src_dir):
    for fname in os.listdir(src_dir):
        if not fname.lower().endswith(('.xlsx', '.xls')):
            continue

        path = os.path.join(src_dir, fname)
        base = os.path.splitext(fname)[0]
        print(f"Processing {fname} → base name '{base}'")

        xl = pd.ExcelFile(path)

        # 1) spatial_{base}.csv ← from 'Edges' sheet: node_Idx_1, node_Idx_2
        if 'Nodes' in xl.sheet_names:
            nodes = xl.parse('Nodes')
            spatial = nodes[['node_X_pix', 'node_Y_pix']]
            spatial_fname = f"spatial_{base}.csv"
            spatial.to_csv(spatial_fname, index=False)
            print(f"  • Wrote {spatial_fname}")
        else:
            print(f"  ⚠️  Sheet 'Nodes' not found in {fname}")
            
        # 2) edges_{base}.csv ← from 'Edges' sheet: EndNodes_1, EndNodes_2, name,
        #    (auto) edge_id, Weight, Length, Width_min, Volume, Type, Distance
        if 'Edges' in xl.sheet_names:
            edges = xl.parse('Edges')
            cols = ['EndNodes_1', 'EndNodes_2', 'name',
                    'Weight', 'Length', 'Width', 'Volume', 'Type', 'Distance']
            edges_df = edges[cols].copy()
            edges_df.insert(3, 'edge_id', range(1, len(edges_df) + 1))
            edges_fname = f"edges_{base}.csv"
            edges_df.to_csv(edges_fname, index=False)
            print(f"  • Wrote {edges_fname}")

        # 3) vertices_{base}.csv ← from 'Nodes' sheet: node_Degree, node_Accessibility, node_ID
        if 'Nodes' in xl.sheet_names:
            nodes = xl.parse('Nodes')
            verts = nodes[['node_Degree', 'node_Accessibility', 'node_ID']]
            verts_fname = f"vertices_{base}.csv"
            verts.to_csv(verts_fname, index=False)
            print(f"  • Wrote {verts_fname}")
        else:
            print(f"  ⚠️  Sheet 'Nodes' not found in {fname}")

if __name__ == "__main__":
    src_directory =  "https://synosys.github.io/animated-fungal-network-growth/uploads"
    if not os.path.isdir(src_directory):
        print(f"Error: source directory not found: {src_directory}")
        exit(1)
    process_excel_files(src_directory)
