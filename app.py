import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import PyMongoError, ServerSelectionTimeoutError

# NyumbaFind Python desktop interface.
# This interface uses the SAME database and four collections created by
# nyumbafind_mongodb.js. It does not replace or rewrite the MongoDB script.

MONGO_URI = "mongodb://localhost:27017/"
DATABASE_NAME = "nyumbaFindDB"

BG = "#F3F6FB"
NAVY = "#142B4A"
BLUE = "#2563EB"
TEAL = "#0F766E"
WHITE = "#FFFFFF"
TEXT = "#1E293B"
MUTED = "#64748B"


class NyumbaFindApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NyumbaFind Uganda | Rental Property Manager")
        self.root.geometry("1180x760")
        self.root.minsize(980, 650)
        self.root.configure(bg=BG)
        self.client = None
        self.db = None
        self.setup_style()
        self.build_layout()
        self.connect_database()

    def setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=WHITE, foreground=TEXT,
                        rowheight=30, fieldbackground=WHITE, borderwidth=0)
        style.configure("Treeview.Heading", background="#E7EEF8",
                        foreground=NAVY, font=("Segoe UI", 10, "bold"), padding=9)
        style.map("Treeview", background=[("selected", "#DBEAFE")],
                  foreground=[("selected", NAVY)])
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", padding=(18, 10),
                        font=("Segoe UI", 10, "bold"))
        style.configure("TCombobox", padding=7)
        style.configure("TEntry", padding=7)

    def build_layout(self):
        header = tk.Frame(self.root, bg=NAVY, height=88)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="NyumbaFind", bg=NAVY, fg=WHITE,
                 font=("Segoe UI", 23, "bold")).pack(side="left", padx=(28, 8), pady=18)
        tk.Label(header, text="UGANDA • FIND A PLACE TO CALL HOME",
                 bg=NAVY, fg="#BFD4F2", font=("Segoe UI", 9, "bold")).pack(side="left", pady=25)
        self.connection_label = tk.Label(header, text="● Connecting...",
                                         bg=NAVY, fg="#FDE68A", font=("Segoe UI", 10, "bold"))
        self.connection_label.pack(side="right", padx=28)

        intro = tk.Frame(self.root, bg=BG)
        intro.pack(fill="x", padx=28, pady=(20, 10))
        tk.Label(intro, text="Rental management dashboard", bg=BG, fg=NAVY,
                 font=("Segoe UI", 19, "bold")).pack(anchor="w")
        tk.Label(intro, text="Search properties, register listings, review reports and manage viewing requests.",
                 bg=BG, fg=MUTED, font=("Segoe UI", 10)).pack(anchor="w", pady=(4, 0))

        cards = tk.Frame(self.root, bg=BG)
        cards.pack(fill="x", padx=28, pady=8)
        self.stat_labels = {}
        for key, title in [("properties", "LISTINGS"), ("users", "REGISTERED USERS"),
                           ("reports", "PROPERTY REPORTS"), ("views", "VIEWING REQUESTS")]:
            card = tk.Frame(cards, bg=WHITE, highlightbackground="#E2E8F0",
                            highlightthickness=1)
            card.pack(side="left", fill="x", expand=True, padx=(0, 12), ipady=10)
            tk.Label(card, text=title, bg=WHITE, fg=MUTED,
                     font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=15, pady=(10, 2))
            value = tk.Label(card, text="-", bg=WHITE, fg=NAVY,
                             font=("Segoe UI", 21, "bold"))
            value.pack(anchor="w", padx=15)
            self.stat_labels[key] = value

        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(fill="both", expand=True, padx=28, pady=(12, 22))
        self.properties_tab = tk.Frame(self.tabs, bg=WHITE)
        self.users_tab = tk.Frame(self.tabs, bg=WHITE)
        self.reports_tab = tk.Frame(self.tabs, bg=WHITE)
        self.viewings_tab = tk.Frame(self.tabs, bg=WHITE)
        self.tabs.add(self.properties_tab, text="Properties")
        self.tabs.add(self.users_tab, text="Users")
        self.tabs.add(self.reports_tab, text="Reports")
        self.tabs.add(self.viewings_tab, text="Viewing requests")
        self.build_properties_tab()
        self.build_simple_tab(self.users_tab, "users",
                              ["_id", "fullName", "phone", "role", "district"])
        self.build_simple_tab(self.reports_tab, "propertyReports",
                              ["_id", "propertyId", "reportedBy", "reason", "status"])
        self.build_simple_tab(self.viewings_tab, "viewingRequests",
                              ["_id", "propertyId", "tenantId", "requestedDate", "status"])

    def button(self, parent, text, command, color=BLUE):
        return tk.Button(parent, text=text, command=command, bg=color, fg=WHITE,
                         activebackground=color, activeforeground=WHITE,
                         relief="flat", padx=14, pady=8,
                         font=("Segoe UI", 9, "bold"), cursor="hand2")

    def build_properties_tab(self):
        top = tk.Frame(self.properties_tab, bg=WHITE)
        top.pack(fill="x", padx=18, pady=16)
        tk.Label(top, text="Find rental properties", bg=WHITE, fg=NAVY,
                 font=("Segoe UI", 13, "bold")).pack(side="left")
        self.search_district = tk.StringVar()
        self.search_max = tk.StringVar()
        ttk.Entry(top, textvariable=self.search_district, width=18).pack(side="left", padx=(20, 6))
        ttk.Entry(top, textvariable=self.search_max, width=14).pack(side="left", padx=6)
        tk.Label(top, text="District", bg=WHITE, fg=MUTED).pack(side="left", padx=(0, 8))
        self.button(top, "Search", self.search_properties).pack(side="left", padx=5)
        self.button(top, "Show all", self.load_properties, TEAL).pack(side="left", padx=5)
        self.button(top, "+ Add property", self.add_property_dialog).pack(side="right")

        # make_tree already packs its own wrapper frame into the tab,
        # so we must NOT call pack() on the tree again.
        self.property_tree = self.make_tree(
            self.properties_tab,
            ["_id", "title", "district", "area", "bedrooms", "monthlyRentUGX",
             "depositUGX", "available", "verificationStatus"],
            [65, 245, 100, 120, 75, 120, 110, 85, 125])

    def build_simple_tab(self, parent, collection, columns):
        bar = tk.Frame(parent, bg=WHITE)
        bar.pack(fill="x", padx=18, pady=14)
        tk.Label(bar, text=collection, bg=WHITE, fg=NAVY,
                 font=("Segoe UI", 13, "bold")).pack(side="left")
        self.button(bar, "Refresh", lambda c=collection: self.load_collection(c), TEAL).pack(side="right")
        tree = self.make_tree(parent, columns,
                              [120 if c in ("_id", "status", "role", "district", "propertyId", "tenantId") else 220
                               for c in columns])
        # The wrapper is already packed by make_tree.
        setattr(self, f"tree_{collection}", tree)

    def make_tree(self, parent, columns, widths):
        wrap = tk.Frame(parent, bg=WHITE)
        # Treeview is returned; parent is the tab.
        tree = ttk.Treeview(wrap, columns=columns, show="headings")
        for col, width in zip(columns, widths):
            tree.heading(col, text=col)
            tree.column(col, width=width, minwidth=65, anchor="w")
        yscroll = ttk.Scrollbar(wrap, orient="vertical", command=tree.yview)
        xscroll = ttk.Scrollbar(wrap, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
        tree.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")
        xscroll.grid(row=1, column=0, sticky="ew")
        wrap.rowconfigure(0, weight=1)
        wrap.columnconfigure(0, weight=1)
        # Keep the wrapper attached to the tree so it can be packed later.
        tree.wrapper = wrap
        wrap.pack(fill="both", expand=True, padx=18, pady=(0, 18))
        return tree

    def connect_database(self):
        try:
            self.client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2500)
            self.client.admin.command("ping")
            self.db = self.client[DATABASE_NAME]
            self.connection_label.config(text="● MongoDB connected", fg="#86EFAC")
            self.refresh_all()
        except Exception as exc:
            self.connection_label.config(text="● MongoDB not connected", fg="#FCA5A5")
            messagebox.showwarning(
                "MongoDB connection",
                "The interface opened, but it cannot reach MongoDB.\n\n"
                "Start MongoDB first, then click Refresh or restart this app.\n\n"
                f"Details: {exc}")

    def require_db(self):
        if self.db is None:
            self.connect_database()
        if self.db is None:
            raise RuntimeError("MongoDB is not connected. Start MongoDB and try again.")

    def refresh_all(self):
        if self.db is None:
            return
        self.load_properties()
        for name in ("users", "propertyReports", "viewingRequests"):
            self.load_collection(name)
        self.update_stats()

    def update_stats(self):
        try:
            self.stat_labels["properties"].config(text=str(self.db.properties.count_documents({})))
            self.stat_labels["users"].config(text=str(self.db.users.count_documents({})))
            self.stat_labels["reports"].config(text=str(self.db.propertyReports.count_documents({})))
            self.stat_labels["views"].config(text=str(self.db.viewingRequests.count_documents({})))
        except PyMongoError:
            pass

    def fill_tree(self, tree, docs, columns):
        for item in tree.get_children():
            tree.delete(item)
        for doc in docs:
            values = []
            for col in columns:
                value = doc.get(col, "")
                if isinstance(value, datetime):
                    value = value.strftime("%Y-%m-%d %H:%M")
                elif isinstance(value, dict):
                    value = str(value)
                values.append(value)
            tree.insert("", "end", values=values)

    def load_properties(self):
        try:
            self.require_db()
            docs = list(self.db.properties.find().sort("_id", 1))
            cols = ["_id", "title", "district", "area", "bedrooms", "monthlyRentUGX",
                    "depositUGX", "available", "verificationStatus"]
            self.fill_tree(self.property_tree, docs, cols)
            self.update_stats()
        except Exception as exc:
            messagebox.showerror("Load properties", str(exc))

    def search_properties(self):
        try:
            self.require_db()
            query = {"available": True}
            district = self.search_district.get().strip()
            maximum = self.search_max.get().strip()
            if district:
                query["district"] = {"$regex": district, "$options": "i"}
            if maximum:
                query["monthlyRentUGX"] = {"$lte": int(maximum)}
            docs = list(self.db.properties.find(query).sort("monthlyRentUGX", 1))
            cols = ["_id", "title", "district", "area", "bedrooms", "monthlyRentUGX",
                    "depositUGX", "available", "verificationStatus"]
            self.fill_tree(self.property_tree, docs, cols)
        except ValueError:
            messagebox.showerror("Invalid amount",
                                 "Maximum rent must be a whole number, for example 300000.")
        except Exception as exc:
            messagebox.showerror("Search", str(exc))

    def load_collection(self, name):
        try:
            self.require_db()
            tree = getattr(self, f"tree_{name}")
            columns = {
                "users": ["_id", "fullName", "phone", "role", "district"],
                "propertyReports": ["_id", "propertyId", "reportedBy", "reason", "status"],
                "viewingRequests": ["_id", "propertyId", "tenantId", "requestedDate", "status"],
            }[name]
            self.fill_tree(tree, list(self.db[name].find().sort("_id", 1)), columns)
            self.update_stats()
        except Exception as exc:
            messagebox.showerror("Load data", str(exc))

    def add_property_dialog(self):
        win = tk.Toplevel(self.root)
        win.title("Add a rental property")
        win.geometry("430x540")
        win.configure(bg=WHITE)
        win.transient(self.root)
        tk.Label(win, text="Register a property", bg=WHITE, fg=NAVY,
                 font=("Segoe UI", 17, "bold")).pack(anchor="w", padx=24, pady=(22, 4))
        tk.Label(win, text="Enter the listing details below.", bg=WHITE, fg=MUTED).pack(
            anchor="w", padx=24, pady=(0, 14))
        fields = {}
        specs = [("Property ID", "id"), ("Title", "title"), ("District", "district"),
                 ("Area", "area"), ("Property type", "type"), ("Bedrooms", "bedrooms"),
                 ("Monthly rent (UGX)", "rent"), ("Deposit (UGX)", "deposit"),
                 ("Advertiser user ID", "advertiser")]
        form = tk.Frame(win, bg=WHITE)
        form.pack(fill="both", expand=True, padx=24)
        for label, key in specs:
            tk.Label(form, text=label, bg=WHITE, fg=TEXT,
                     font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(5, 2))
            entry = ttk.Entry(form)
            entry.pack(fill="x")
            fields[key] = entry

        def save():
            try:
                self.require_db()
                doc = {
                    "_id": fields["id"].get().strip(),
                    "title": fields["title"].get().strip(),
                    "district": fields["district"].get().strip(),
                    "area": fields["area"].get().strip(),
                    "propertyType": fields["type"].get().strip(),
                    "bedrooms": int(fields["bedrooms"].get()),
                    "monthlyRentUGX": int(fields["rent"].get()),
                    "depositUGX": int(fields["deposit"].get()),
                    "available": True,
                    "verificationStatus": "pending",
                    "advertiserId": fields["advertiser"].get().strip(),
                }
                if not all([doc["_id"], doc["title"], doc["district"], doc["advertiserId"]]):
                    raise ValueError("Complete all required fields.")
                self.db.properties.insert_one(doc)
                messagebox.showinfo("Saved", "Property added. Its verification status is PENDING.")
                win.destroy()
                self.load_properties()
            except Exception as exc:
                messagebox.showerror("Could not save property", str(exc))

        self.button(win, "Save property", save).pack(fill="x", padx=24, pady=20)


if __name__ == "__main__":
    root = tk.Tk()
    app = NyumbaFindApp(root)
    root.mainloop()
