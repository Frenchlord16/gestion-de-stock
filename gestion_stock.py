import tkinter as tk
from tkinter import ttk, messagebox
import json, os, datetime

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stock_data.json")

def load():
    try:
        with open(DATA, "r", encoding="utf-8") as f: return json.load(f)
    except: return {"products": [], "history": []}

data = load()

def save():
    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    refresh()

def money(v): return f"{float(v):,.2f} €".replace(",", " ").replace(".", ",")

rootwin = tk.Tk()
rootwin.title("Gestion Stock - Marchandises")
rootwin.geometry("1200x720")
rootwin.minsize(1000, 620)

style=ttk.Style()
try: style.theme_use("clam")
except: pass
style.configure("Title.TLabel", font=("Segoe UI", 22, "bold"))
style.configure("Card.TFrame", background="#ffffff")
style.configure("CardTitle.TLabel", background="#ffffff", foreground="#667085", font=("Segoe UI", 10))
style.configure("CardValue.TLabel", background="#ffffff", foreground="#172033", font=("Segoe UI", 20, "bold"))
style.configure("Treeview", rowheight=34, font=("Segoe UI", 10))
style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

rootwin.configure(bg="#f3f5f8")
header=ttk.Frame(rootwin, padding=18)
header.pack(fill="x")
ttk.Label(header,text="📦 Gestion Stock",style="Title.TLabel").pack(side="left")
ttk.Label(header,text="  Gestion de marchandises",font=("Segoe UI",11)).pack(side="left")

notebook=ttk.Notebook(rootwin)
notebook.pack(fill="both",expand=True,padx=18,pady=(0,18))

# DASHBOARD
dash=ttk.Frame(notebook,padding=18); notebook.add(dash,text="  🏠 Tableau de bord  ")
cards=ttk.Frame(dash); cards.pack(fill="x",pady=(0,18))
vars_cards=[]
for i,(title,key) in enumerate([("Produits","products"),("Unités en stock","units"),("Valeur du stock","value"),("Stock faible","low")]):
    f=ttk.Frame(cards,padding=16,style="Card.TFrame"); f.grid(row=0,column=i,sticky="nsew",padx=6)
    cards.columnconfigure(i,weight=1)
    ttk.Label(f,text=title,style="CardTitle.TLabel").pack(anchor="w")
    v=tk.StringVar(value="0"); vars_cards.append(v)
    ttk.Label(f,textvariable=v,style="CardValue.TLabel").pack(anchor="w",pady=(7,0))

info=ttk.LabelFrame(dash,text=" Résumé ",padding=15); info.pack(fill="both",expand=True)
summary=tk.StringVar()
ttk.Label(info,textvariable=summary,font=("Segoe UI",12),justify="left").pack(anchor="nw")

# STOCK
stock=ttk.Frame(notebook,padding=15); notebook.add(stock,text="  📦 Stock  ")
bar=ttk.Frame(stock); bar.pack(fill="x",pady=(0,10))
search=tk.StringVar()
ttk.Label(bar,text="Rechercher :").pack(side="left")
ttk.Entry(bar,textvariable=search,width=35).pack(side="left",padx=8)
ttk.Button(bar,text="＋ Ajouter",command=lambda:add_product()).pack(side="right")
ttk.Button(bar,text="✎ Modifier",command=lambda:edit_selected()).pack(side="right",padx=5)
ttk.Button(bar,text="🗑 Supprimer",command=lambda:delete_selected()).pack(side="right")

cols=("name","ref","cat","qty","threshold","buy","sell","value")
tree=ttk.Treeview(stock,columns=cols,show="headings")
heads={"name":"Produit","ref":"Référence","cat":"Catégorie","qty":"Stock","threshold":"Seuil","buy":"Achat","sell":"Vente","value":"Valeur"}
for c in cols: tree.heading(c,text=heads[c])
for c,w in {"name":190,"ref":110,"cat":120,"qty":70,"threshold":70,"buy":90,"sell":90,"value":100}.items(): tree.column(c,width=w)
tree.pack(fill="both",expand=True)
tree.tag_configure("low",foreground="#c62828")

# MOVEMENTS
mov=ttk.Frame(notebook,padding=15); notebook.add(mov,text="  🔄 Entrées / Sorties  ")
mbar=ttk.Frame(mov); mbar.pack(fill="x",pady=(0,10))
ttk.Button(mbar,text="＋ Entrée de stock",command=lambda:movement(1)).pack(side="left")
ttk.Button(mbar,text="− Sortie de stock",command=lambda:movement(-1)).pack(side="left",padx=8)
ttk.Label(mbar,text="Sélectionne d'abord un produit dans l'onglet Stock.").pack(side="left",padx=10)
mtree=ttk.Treeview(mov,columns=("date","product","type","qty"),show="headings")
for c,t in zip(("date","product","type","qty"),("Date","Produit","Mouvement","Quantité")): mtree.heading(c,text=t)
mtree.pack(fill="both",expand=True)

# SUPPLIERS
sup=ttk.Frame(notebook,padding=15); notebook.add(sup,text="  🚚 Fournisseurs  ")
ttk.Label(sup,text="Les fournisseurs peuvent être ajoutés depuis cette page.").pack(anchor="w",pady=(0,10))
stree=ttk.Treeview(sup,columns=("name","phone","mail","notes"),show="headings")
for c,t in zip(("name","phone","mail","notes"),("Fournisseur","Téléphone","E-mail","Notes")): stree.heading(c,text=t)
stree.pack(fill="both",expand=True)
supdata=data.setdefault("suppliers",[])
def add_supplier():
    win=tk.Toplevel(rootwin); win.title("Ajouter fournisseur"); win.grab_set()
    entries=[]
    for label in ["Nom","Téléphone","E-mail","Notes"]:
        ttk.Label(win,text=label).pack(anchor="w",padx=15,pady=(10,2))
        e=ttk.Entry(win,width=45); e.pack(padx=15); entries.append(e)
    def ok():
        supdata.append({"name":entries[0].get(),"phone":entries[1].get(),"mail":entries[2].get(),"notes":entries[3].get()}); save(); win.destroy()
    ttk.Button(win,text="Enregistrer",command=ok).pack(pady=15)
ttk.Button(sup,text="＋ Ajouter un fournisseur",command=add_supplier).pack(anchor="e",pady=8)

def product_form(existing=None):
    win=tk.Toplevel(rootwin); win.title("Produit"); win.grab_set()
    labels=["Nom","Référence","Catégorie","Quantité","Seuil d'alerte","Prix achat (€)","Prix vente (€)","Emplacement"]
    vals=[existing.get("name","") if existing else "",existing.get("ref","") if existing else "",existing.get("cat","") if existing else "",
          str(existing.get("qty",0)) if existing else "0",str(existing.get("threshold",5)) if existing else "5",
          str(existing.get("buy",0)) if existing else "0",str(existing.get("sell",0)) if existing else "0",existing.get("location","") if existing else ""]
    es=[]
    for l,v in zip(labels,vals):
        ttk.Label(win,text=l).pack(anchor="w",padx=15,pady=(8,2)); e=ttk.Entry(win,width=42); e.insert(0,v); e.pack(padx=15); es.append(e)
    def ok():
        try:
            p={"name":es[0].get().strip(),"ref":es[1].get().strip(),"cat":es[2].get().strip(),
               "qty":int(es[3].get()),"threshold":int(es[4].get()),"buy":float(es[5].get().replace(",",".")),
               "sell":float(es[6].get().replace(",",".")),"location":es[7].get().strip()}
            if not p["name"]: raise ValueError()
            if existing: existing.update(p)
            else: data["products"].append(p)
            save(); win.destroy()
        except: messagebox.showerror("Erreur","Vérifie les champs numériques et le nom du produit.")
    ttk.Button(win,text="Enregistrer",command=ok).pack(pady=15)

def add_product(): product_form()
def selected_product():
    s=tree.selection()
    if not s: return None
    return data["products"][tree.index(s[0])]
def edit_selected():
    p=selected_product()
    if p: product_form(p)
    else: messagebox.showinfo("Stock","Sélectionne un produit.")
def delete_selected():
    p=selected_product()
    if p and messagebox.askyesno("Supprimer","Supprimer ce produit ?"):
        data["products"].remove(p); save()
def movement(direction):
    p=selected_product()
    if not p: messagebox.showinfo("Stock","Sélectionne un produit dans l'onglet Stock."); return
    win=tk.Toplevel(rootwin); win.title("Mouvement de stock"); win.grab_set()
    ttk.Label(win,text=f"{'Entrée' if direction==1 else 'Sortie'} — {p['name']}").pack(padx=20,pady=15)
    e=ttk.Entry(win); e.insert(0,"1"); e.pack(padx=20)
    def ok():
        try:
            n=int(e.get())
            if n<=0 or (direction<0 and p["qty"]<n): raise ValueError()
            p["qty"]+=direction*n
            data["history"].append({"date":datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),"product":p["name"],"type":"Entrée" if direction==1 else "Sortie","qty":n})
            save(); win.destroy()
        except: messagebox.showerror("Erreur","Quantité invalide ou stock insuffisant.")
    ttk.Button(win,text="Valider",command=ok).pack(pady=15)

def refresh():
    for i in tree.get_children(): tree.delete(i)
    q=search.get().lower()
    for p in data["products"]:
        if q and q not in (p["name"]+" "+p["ref"]+" "+p["cat"]).lower(): continue
        iid=tree.insert("", "end", values=(p["name"],p["ref"],p["cat"],p["qty"],p["threshold"],money(p["buy"]),money(p["sell"]),money(p["qty"]*p["buy"])))
        if p["qty"]<=p["threshold"]: tree.item(iid,tags=("low",))
    for i in mtree.get_children(): mtree.delete(i)
    for h in reversed(data["history"]): mtree.insert("", "end", values=(h["date"],h["product"],h["type"],h["qty"]))
    for i in stree.get_children(): stree.delete(i)
    for s in data.get("suppliers",[]): stree.insert("", "end", values=(s.get("name",""),s.get("phone",""),s.get("mail",""),s.get("notes","")))
    units=sum(p["qty"] for p in data["products"]); val=sum(p["qty"]*p["buy"] for p in data["products"]); low=sum(p["qty"]<=p["threshold"] for p in data["products"])
    vars_cards[0].set(str(len(data["products"])));vars_cards[1].set(str(units));vars_cards[2].set(money(val));vars_cards[3].set(str(low))
    summary.set(f"Produits enregistrés : {len(data['products'])}\\nUnités disponibles : {units}\\nValeur d'achat du stock : {money(val)}\\nProduits sous leur seuil : {low}\\n\\nConseil : utilise l'onglet « Entrées / Sorties » pour garder un historique des mouvements.")
search.trace_add("write",lambda *a:refresh())
refresh()
rootwin.mainloop()
