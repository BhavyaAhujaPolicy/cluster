import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import pyperclip
import os

EXCEL_FILE = 'output_clusters.xlsx'

# Load and structure data per cluster
def load_data():
    df = pd.read_excel(EXCEL_FILE)
    grouped = {}
    for _, row in df.iterrows():
        cid = row['ClusterIndex']
        if cid not in grouped:
            grouped[cid] = {
                'meta': {
                    'AgeGroup': row['AgeGroup'],
                    'Gender': row['Gender'],
                    'IncomeGroup': row['IncomeGroup'],
                    'Profession': row['Profession'],
                    'City': row['City'],
                    'Brand': row['Brand'],
                    'LeadCount': row['LeadCount']
                },
                'slots': []
            }
        grouped[cid]['slots'].append({
            'Day': row['Day'],
            'Time': row['Time'],
            'PickupRate': row['PickupRate'],
            'AvgDuration': row['AvgDuration'],
            'BestTime': row['BestTime']
        })
    return grouped

# Copy to clipboard function
def copy_row_to_clipboard(cluster_meta):
    formatted = " | ".join(f"{k}: {v}" for k, v in cluster_meta.items())
    pyperclip.copy(formatted)
    messagebox.showinfo("Copied", "Cluster details copied to clipboard!")

# Export options

def export_data(data):
    export_df = []
    for cid, info in data.items():
        for slot in info['slots']:
            export_df.append({**{'ClusterIndex': cid}, **info['meta'], **slot})
    df = pd.DataFrame(export_df)

    def save(format):
        ext = format.lower()
        file = filedialog.asksaveasfilename(defaultextension=f".{ext}", filetypes=[(f"{format} files", f"*.{ext}")])
        if not file:
            return
        if ext == 'csv':
            df.to_csv(file, index=False)
        elif ext == 'xlsx':
            df.to_excel(file, index=False)
        elif ext == 'json':
            df.to_json(file, orient='records', indent=2)
        messagebox.showinfo("Exported", f"Data exported as {format.upper()}.")

    return save

# GUI creation
def create_gui():
    data = load_data()

    root = tk.Tk()
    root.title("Cluster Viewer Pro")
    root.geometry("1250x720")

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview", rowheight=30, font=('Segoe UI', 10))
    style.configure("Treeview.Heading", font=('Segoe UI', 10, 'bold'))

    tree = ttk.Treeview(root)
    tree.pack(fill='both', expand=True)

    # Scrollbars
    vsb = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
    vsb.pack(side='right', fill='y')
    tree.configure(yscrollcommand=vsb.set)

    tree['columns'] = (
        "AgeGroup", "Gender", "IncomeGroup", "Profession",
        "City", "Brand", "LeadCount"
    )
    tree.heading("#0", text="ClusterIndex")
    for col in tree['columns']:
        tree.heading(col, text=col)
        tree.column(col, anchor='center', width=120)
    tree.column("#0", anchor='center', width=100)

    for cid, info in data.items():
        cluster_meta = info['meta']
        parent = tree.insert("", "end", iid=f"cluster_{cid}", text=str(cid),
                             values=[
                                 cluster_meta['AgeGroup'], cluster_meta['Gender'], cluster_meta['IncomeGroup'],
                                 cluster_meta['Profession'], cluster_meta['City'], cluster_meta['Brand'], cluster_meta['LeadCount']
                             ])

        # Add children (time slots), hidden until expanded
        for slot in info['slots']:
            tree.insert(parent, 'end', text='',
                        values=[slot['Day'], slot['Time'], slot['PickupRate'], slot['AvgDuration'], slot['BestTime'], '', ''])

        # Add Copy button as last child
        btn = ttk.Button(tree, text="Copy", width=6,
                         command=lambda m=cluster_meta: copy_row_to_clipboard(m))
        tree.insert(parent, 'end', text='[Copy this]', values=[''] * 7)

    # Export buttons
    btn_frame = ttk.Frame(root)
    btn_frame.pack(fill='x', pady=10)
    for fmt in ['CSV', 'Excel', 'JSON']:
        ttk.Button(btn_frame, text=f"Export {fmt}", width=20,
                   command=export_data(data)).pack(side='left', padx=10)

    root.mainloop()

if __name__ == "__main__":
    try:
        import pyperclip
    except ImportError:
        os.system("pip install pyperclip")
        import pyperclip
    create_gui()
