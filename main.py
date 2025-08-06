from data_loader import load_data, preprocess, stream_json_chunks
from cluster_creator import generate_clusters
from export_excel import export_to_excel
from config import DATA_PATH
import os
import pandas as pd
import sys

def main():
    """
    Main workflow: load data in chunks, allow interrupt (Ctrl+C) to checkout, cluster, and export.
    No prompt after each chunk; background listening only.
    """
    print("\U0001F4CA Generating Micro-Clusters and Time Slot Insights...\n")
    total_rows = 1320000  
    chunk_size = 1250000
    dfs = []  # Collect all chunks here
    try:
        for i, df_chunk in enumerate(stream_json_chunks(DATA_PATH, chunk_size=chunk_size, total_rows=total_rows)):
            dfs.append(df_chunk)
    except KeyboardInterrupt:
        print("\n\u26A0\uFE0F Interrupted! Proceeding with loaded data so far...")
    if not dfs:
        print("No data loaded. Exiting.")
        return
    # Concatenate all chunks at once for efficiency
    df = pd.concat(dfs, ignore_index=True)
    print(f"Df description ",df.info())
    print(f"\n\U0001F50D Clustering {len(df):,} rows...")
    clusters = generate_clusters(df)
    export_to_excel(clusters)
    print("\u2705 Clustering Complete. Output saved to 'output_clusters.xlsx'.")

if __name__ == "__main__":
    main()
