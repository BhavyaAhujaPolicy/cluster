# cluster_gui.py

import customtkinter as ctk
import threading
import pandas as pd
from data_loader import load_data, preprocess, stream_json_chunks
from cluster_creator import generate_clusters
from export_excel import export_to_excel
from config import DATA_PATH
import sys

def run_pipeline(update_status):
    update_status("🔄 Loading data in chunks...")
    total_rows = 1320000
    chunk_size = 1250000
    dfs = []
    try:
        for i, df_chunk in enumerate(stream_json_chunks(DATA_PATH, chunk_size=chunk_size, total_rows=total_rows)):
            dfs.append(df_chunk)
    except KeyboardInterrupt:
        update_status("⚠️ Interrupted! Proceeding with loaded data so far...")

    if not dfs:
        update_status("❌ No data loaded. Exiting.")
        return

    df = pd.concat(dfs, ignore_index=True)
    print(df.info())
    update_status(f"🔍 Clustering {len(df):,} rows...")

    clusters = generate_clusters(df)

    update_status("📤 Exporting to Excel...")
    export_to_excel(clusters)

    update_status("✅ Done! Output saved to 'output_clusters.xlsx'.")

def start_process():
    status_label.configure(text="Running...")
    run_button.configure(state="disabled")
    threading.Thread(target=run_with_status).start()

def run_with_status():
    def update_status(text):
        status_label.configure(text=text)
    run_pipeline(update_status)
    run_button.configure(state="normal")

# Setup GUI
ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("480x300")
app.title("📊 Micro-Cluster Generator")

title = ctk.CTkLabel(app, text="📊 Micro-Cluster Generator", font=("Arial", 20, "bold"))
title.pack(pady=20)

run_button = ctk.CTkButton(app, text="▶️ Run Clustering", command=start_process, width=220)
run_button.pack(pady=10)

status_label = ctk.CTkLabel(app, text="Ready", font=("Arial", 14))
status_label.pack(pady=20)

exit_button = ctk.CTkButton(app, text="❌ Exit", command=app.destroy, fg_color="red", hover_color="darkred")
exit_button.pack(pady=5)

app.mainloop()
