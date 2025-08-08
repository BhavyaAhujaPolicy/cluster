import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import pyperclip
import os
from tkinter import simpledialog

EXCEL_FILE = 'output_clusters.xlsx'

# Load and structure data per cluster
def load_data():
    try:
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
    except Exception as e:
        messagebox.showerror("Error", f"Could not load data: {str(e)}")
        return {}

# Copy to clipboard function
def copy_row_to_clipboard(cluster_meta):
    formatted = " | ".join(f"{k}: {v}" for k, v in cluster_meta.items())
    pyperclip.copy(formatted)
    messagebox.showinfo("Copied", "Cluster details copied to clipboard!")

def copy_slot_to_clipboard(slot_data):
    formatted = f"Day: {slot_data['Day']} | Time: {slot_data['Time']} | Pickup Rate: {slot_data['PickupRate']} | Avg Duration: {slot_data['AvgDuration']} | Best Time: {slot_data['BestTime']}"
    pyperclip.copy(formatted)
    messagebox.showinfo("Copied", "Time slot details copied to clipboard!")

# Export functions
def export_to_csv(data):
    export_df = []
    for cid, info in data.items():
        for slot in info['slots']:
            export_df.append({**{'ClusterIndex': cid}, **info['meta'], **slot})
    df = pd.DataFrame(export_df)
    
    file = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if file:
        df.to_csv(file, index=False)
        messagebox.showinfo("Exported", "Data exported as CSV.")

def export_to_excel(data):
    export_df = []
    for cid, info in data.items():
        for slot in info['slots']:
            export_df.append({**{'ClusterIndex': cid}, **info['meta'], **slot})
    df = pd.DataFrame(export_df)
    
    file = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
    if file:
        df.to_excel(file, index=False)
        messagebox.showinfo("Exported", "Data exported as Excel.")

def export_to_json(data):
    export_df = []
    for cid, info in data.items():
        for slot in info['slots']:
            export_df.append({**{'ClusterIndex': cid}, **info['meta'], **slot})
    df = pd.DataFrame(export_df)
    
    file = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
    if file:
        df.to_json(file, orient='records', indent=2)
        messagebox.showinfo("Exported", "Data exported as JSON.")

class SearchDialog:
    def __init__(self, parent):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Search")
        self.dialog.geometry("400x150")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        # Search entry
        tk.Label(self.dialog, text="Search for:").pack(pady=5)
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(self.dialog, textvariable=self.search_var, width=40)
        self.search_entry.pack(pady=5)
        self.search_entry.focus()
        
        # Buttons
        btn_frame = tk.Frame(self.dialog)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Find Next", command=self.find_next).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Find Previous", command=self.find_previous).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Close", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        self.search_var.trace('w', self.on_search_change)
        self.current_match = 0
        self.matches = []
        
    def on_search_change(self, *args):
        self.current_match = 0
        self.matches = []
        
    def find_next(self):
        # Implementation for finding next match
        pass
        
    def find_previous(self):
        # Implementation for finding previous match
        pass

class ClusterViewerGUI:
    def __init__(self):
        self.data = load_data()
        self.filtered_data = self.data.copy()
        self.search_dialog = None
        
        self.root = tk.Tk()
        self.root.title("Cluster Viewer Pro")
        self.root.geometry("1400x800")
        
        # Bind Ctrl+F
        self.root.bind('<Control-f>', self.show_search_dialog)
        
        self.setup_styles()
        self.create_widgets()
        self.populate_tree()
        
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", rowheight=30, font=('Segoe UI', 10))
        style.configure("Treeview.Heading", font=('Segoe UI', 10, 'bold'))
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Filter frame
        filter_frame = ttk.LabelFrame(main_frame, text="Filters", padding=10)
        filter_frame.pack(fill='x', pady=(0, 10))
        
        # Filter controls
        filter_controls = ttk.Frame(filter_frame)
        filter_controls.pack(fill='x')
        
        # Age Group filter
        ttk.Label(filter_controls, text="Age Group:").grid(row=0, column=0, padx=(0, 5), pady=5)
        self.age_var = tk.StringVar()
        self.age_combo = ttk.Combobox(filter_controls, textvariable=self.age_var, width=15)
        self.age_combo.grid(row=0, column=1, padx=(0, 10), pady=5)
        
        # Gender filter
        ttk.Label(filter_controls, text="Gender:").grid(row=0, column=2, padx=(0, 5), pady=5)
        self.gender_var = tk.StringVar()
        self.gender_combo = ttk.Combobox(filter_controls, textvariable=self.gender_var, width=15)
        self.gender_combo.grid(row=0, column=3, padx=(0, 10), pady=5)
        
        # City filter
        ttk.Label(filter_controls, text="City:").grid(row=0, column=4, padx=(0, 5), pady=5)
        self.city_var = tk.StringVar()
        self.city_combo = ttk.Combobox(filter_controls, textvariable=self.city_var, width=15)
        self.city_combo.grid(row=0, column=5, padx=(0, 10), pady=5)
        
        # Search frame
        search_frame = ttk.Frame(filter_frame)
        search_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=40)
        self.search_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.search_entry.bind('<KeyRelease>', self.on_search)
        
        ttk.Button(search_frame, text="Clear Filters", command=self.clear_filters).pack(side=tk.RIGHT)
        
        # Tree frame
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill='both', expand=True)
        
        # Create treeview
        self.tree = ttk.Treeview(tree_frame)
        self.tree.pack(side='left', fill='both', expand=True)
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        vsb.pack(side='right', fill='y')
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        hsb.pack(side='bottom', fill='x')
        
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Export buttons frame
        export_frame = ttk.Frame(main_frame)
        export_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Button(export_frame, text="Export CSV", command=lambda: export_to_csv(self.filtered_data)).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(export_frame, text="Export Excel", command=lambda: export_to_excel(self.filtered_data)).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(export_frame, text="Export JSON", command=lambda: export_to_json(self.filtered_data)).pack(side=tk.LEFT, padx=(0, 10))
        
        # Populate filter options
        self.populate_filter_options()
        
    def populate_filter_options(self):
        age_groups = sorted(list(set(str(info['meta']['AgeGroup']) for info in self.data.values())))
        genders = sorted(list(set(str(info['meta']['Gender']) for info in self.data.values())))
        cities = sorted(list(set(str(info['meta']['City']) for info in self.data.values())))
        
        self.age_combo['values'] = ['All'] + age_groups
        self.gender_combo['values'] = ['All'] + genders
        self.city_combo['values'] = ['All'] + cities
        
        self.age_combo.set('All')
        self.gender_combo.set('All')
        self.city_combo.set('All')
        
        # Bind filter changes
        self.age_var.trace('w', self.apply_filters)
        self.gender_var.trace('w', self.apply_filters)
        self.city_var.trace('w', self.apply_filters)
        
    def apply_filters(self, *args):
        self.filtered_data = {}
        
        for cid, info in self.data.items():
            meta = info['meta']
            
            # Apply filters
            if self.age_var.get() != 'All' and meta['AgeGroup'] != self.age_var.get():
                continue
            if self.gender_var.get() != 'All' and meta['Gender'] != self.gender_var.get():
                continue
            if self.city_var.get() != 'All' and meta['City'] != self.city_var.get():
                continue
                
            self.filtered_data[cid] = info
            
        self.populate_tree()
        
    def on_search(self, event=None):
        search_term = self.search_var.get().lower()
        if not search_term:
            self.apply_filters()
            return
            
        self.filtered_data = {}
        
        for cid, info in self.data.items():
            meta = info['meta']
            searchable_text = f"{meta['AgeGroup']} {meta['Gender']} {meta['IncomeGroup']} {meta['Profession']} {meta['City']} {meta['Brand']}".lower()
            
            if search_term in searchable_text:
                self.filtered_data[cid] = info
                
        self.populate_tree()
        
    def clear_filters(self):
        self.age_var.set('All')
        self.gender_var.set('All')
        self.city_var.set('All')
        self.search_var.set('')
        self.filtered_data = self.data.copy()
        self.populate_tree()
        
    def populate_tree(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Configure columns
        self.tree['columns'] = (
            "AgeGroup", "Gender", "IncomeGroup", "Profession",
            "City", "Brand", "LeadCount", "Actions"
        )
        
        self.tree.heading("#0", text="Cluster Index")
        for col in self.tree['columns']:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor='center', width=120)
            
        self.tree.column("#0", anchor='center', width=100)
        self.tree.column("Actions", width=80)
        
        # Populate data
        for cid, info in self.filtered_data.items():
            cluster_meta = info['meta']
            parent = self.tree.insert("", "end", iid=f"cluster_{cid}", text=str(cid),
                                     values=[
                                         cluster_meta['AgeGroup'], cluster_meta['Gender'], 
                                         cluster_meta['IncomeGroup'], cluster_meta['Profession'],
                                         cluster_meta['City'], cluster_meta['Brand'], 
                                         cluster_meta['LeadCount'], ""
                                     ])
            
                        # Add time slots as children
            for i, slot in enumerate(info['slots']):
                slot_id = f"slot_{cid}_{i}"
                pickup_rate = slot['PickupRate']
                avg_duration = slot['AvgDuration']
                
                # Handle numeric formatting safely
                pickup_str = f"{pickup_rate:.2f}%" if isinstance(pickup_rate, (int, float)) else str(pickup_rate)
                duration_str = f"{avg_duration:.1f}min" if isinstance(avg_duration, (int, float)) else str(avg_duration)
                
                self.tree.insert(parent, 'end', iid=slot_id, text=f"Slot {i+1}",
                                values=[
                                    slot['Day'], slot['Time'], pickup_str,
                                    duration_str, slot['BestTime'],
                                    "", "", "Copy"
                                ])
                
                # Bind copy action for slots
                self.tree.tag_bind(slot_id, '<Double-1>', lambda e, s=slot: copy_slot_to_clipboard(s))
            
            # Add copy button for cluster
            copy_id = f"copy_{cid}"
            self.tree.insert(parent, 'end', iid=copy_id, text="[Copy Cluster]",
                            values=["", "", "", "", "", "", "", "Copy"])
            self.tree.tag_bind(copy_id, '<Double-1>', lambda e, m=cluster_meta: copy_row_to_clipboard(m))
            
    def show_search_dialog(self, event=None):
        if self.search_dialog is None or not self.search_dialog.dialog.winfo_exists():
            self.search_dialog = SearchDialog(self.root)
        else:
            self.search_dialog.dialog.lift()
            
    def run(self):
        self.root.mainloop()

def create_gui():
    app = ClusterViewerGUI()
    app.run()

if __name__ == "__main__":
    try:
        import pyperclip
    except ImportError:
        os.system("pip install pyperclip")
        import pyperclip
    create_gui()
