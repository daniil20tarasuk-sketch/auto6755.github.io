import customtkinter as ctk
import os
import json
import shutil
import re
import webbrowser
from tkinter import messagebox, filedialog

ctk.set_appearance_mode("dark")

class AutoManager(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AUTO67 — Управление Магазином")
        self.geometry("1100x950")

        self.cur_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = os.path.join(self.cur_dir, "data")
        self.prod_dir = os.path.join(self.data_dir, "products")
        self.img_dir = os.path.join(self.cur_dir, "img", "parts")
        
        self.files = {
            "brands": os.path.join(self.data_dir, "brands.js"),
            "models": os.path.join(self.data_dir, "models.js"),
            "kat": os.path.join(self.data_dir, "kat.js"),
            "config": os.path.join(self.data_dir, "config.js")
        }
        
        self.temp_images = []
        self.ensure_folders()
        self.setup_ui()

    def ensure_folders(self):
        for d in [self.data_dir, self.prod_dir, self.img_dir]:
            os.makedirs(d, exist_ok=True)

    def read_js(self, path):
        is_list_type = "brands.js" in path or "products" in path
        if not os.path.exists(path): 
            return [] if is_list_type else {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if "=" not in content: return [] if is_list_type else {}
                json_str = content.split("=", 1)[1].strip().rstrip(";")
                return json.loads(json_str)
        except Exception as e: 
            return [] if is_list_type else {}

    def write_js(self, path, var_name, data):
        with open(path, "w", encoding="utf-8") as f:
            if "PRODUCTS_" in var_name:
                f.write(f"window['{var_name}'] = {json.dumps(data, ensure_ascii=False, indent=4)};")
            else:
                f.write(f"const {var_name} = {json.dumps(data, ensure_ascii=False, indent=4)};")

    def setup_ui(self):
        self.tabs = ctk.CTkTabview(self)
        self.tabs.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tab_add = self.tabs.add("➕ Добавление")
        self.tab_delete = self.tabs.add("🗑️ Удаление")
        self.tab_settings = self.tabs.add("⚙️ Настройки")
        
        ctk.CTkButton(self.tab_add, text="+ Добавить Марку", command=self.add_brand_win).pack(pady=10)
        ctk.CTkButton(self.tab_add, text="+ Добавить Модель", command=self.add_model_win).pack(pady=10)
        ctk.CTkButton(self.tab_add, text="+ Добавить Категорию (Тип)", command=self.add_kat_win).pack(pady=10)
        ctk.CTkButton(self.tab_add, text="📦 ДОБАВИТЬ ЗАПЧАСТЬ", height=60, fg_color="#27ae60", command=self.add_part_win).pack(pady=20)
        
        ctk.CTkLabel(self.tab_add, text="Массовое копирование:", font=("Arial", 12, "bold")).pack(pady=(10,0))
        ctk.CTkButton(self.tab_add, text="📋 Копировать категории", command=self.copy_categories_win).pack(pady=5)
        ctk.CTkButton(self.tab_add, text="📦 Копировать все товары модели", command=self.copy_products_win).pack(pady=5)

        ctk.CTkLabel(self.tab_delete, text="Выберите, что удалить:", font=("Arial", 16, "bold")).pack(pady=10)
        ctk.CTkButton(self.tab_delete, text="❌ Удалить Марку", fg_color="#c0392b", command=self.del_brand_win).pack(pady=5)
        ctk.CTkButton(self.tab_delete, text="❌ Удалить Модель", fg_color="#c0392b", command=self.del_model_win).pack(pady=5)
        ctk.CTkButton(self.tab_delete, text="❌ Удалить Тип запчасти", fg_color="#c0392b", command=self.del_kat_win).pack(pady=5)
        ctk.CTkButton(self.tab_delete, text="🗑️ ВЫБРАТЬ И УДАЛИТЬ ЗАПЧАСТИ", height=60, fg_color="#e74c3c", command=self.del_part_list_win).pack(pady=20)

        self.render_settings_tab()

    def del_part_list_win(self):
        brands = self.read_js(self.files["brands"])
        models_dict = self.read_js(self.files["models"])
        if not brands: return
        win = ctk.CTkToplevel(self); win.title("Выбор запчастей для удаления"); win.geometry("600x800"); win.attributes("-topmost", True)
        b_var = ctk.StringVar(value=brands[0]['name'])
        ctk.CTkOptionMenu(win, values=[b['name'] for b in brands], variable=b_var).pack(pady=5)
        m_var = ctk.StringVar()
        m_menu = ctk.CTkOptionMenu(win, variable=m_var); m_menu.pack(pady=5)
        scroll = ctk.CTkScrollableFrame(win, width=550, height=500); scroll.pack(pady=10, padx=10, fill="both", expand=True)
        checks = {}
        def refresh_list(*a):
            for w in scroll.winfo_children(): w.destroy()
            checks.clear()
            bid = next((b['id'] for b in brands if b['name'] == b_var.get()), "")
            mid = m_var.get().lower().replace(" ", "_")
            path = os.path.join(self.prod_dir, f"{bid}_{mid}.js")
            data = self.read_js(path)
            for i, p in enumerate(data):
                var = ctk.BooleanVar()
                cb = ctk.CTkCheckBox(scroll, text=f"{p['brand']} - {p['art']} ({p['price']}р)", variable=var); cb.pack(anchor="w", pady=2)
                checks[i] = var
        def up_m(*a):
            bid = next(b['id'] for b in brands if b['name'] == b_var.get())
            ms = [m['name'] for m in models_dict.get(bid, [])]
            m_menu.configure(values=ms)
            if ms: m_var.set(ms[0])
        b_var.trace("w", up_m); m_var.trace("w", refresh_list); up_m()
        def do_delete():
            bid = next((b['id'] for b in brands if b['name'] == b_var.get()), "")
            mid = m_var.get().lower().replace(" ", "_")
            path = os.path.join(self.prod_dir, f"{bid}_{mid}.js")
            data = self.read_js(path)
            new_data = [p for i, p in enumerate(data) if not checks[i].get()]
            if len(new_data) != len(data):
                var_name = f"PRODUCTS_{bid.upper()}_{mid.upper()}"
                self.write_js(path, var_name, new_data)
                messagebox.showinfo("ОК", f"Удалено {len(data)-len(new_data)} запчастей"); win.destroy()
        ctk.CTkButton(win, text="УДАЛИТЬ ВЫБРАННЫЕ", fg_color="red", command=do_delete).pack(pady=10)

    def copy_products_win(self):
        brands = self.read_js(self.files["brands"])
        models_dict = self.read_js(self.files["models"])
        all_models = []
        for bid in models_dict:
            for m in models_dict[bid]: all_models.append(f"{bid} | {m['name']}")
        if not all_models: return
        win = ctk.CTkToplevel(self); win.title("Копирование товаров"); win.geometry("450x450"); win.attributes("-topmost", True)
        ctk.CTkLabel(win, text="ОТКУДА (Донор):").pack()
        src_v = ctk.StringVar(value=all_models[0]); ctk.CTkOptionMenu(win, values=all_models, variable=src_v).pack(pady=5)
        ctk.CTkLabel(win, text="КУДА (Цель):").pack()
        dst_v = ctk.StringVar(value=all_models[0]); ctk.CTkOptionMenu(win, values=all_models, variable=dst_v).pack(pady=5)
        def run():
            s_bid, s_m = src_v.get().split(" | "); d_bid, d_m = dst_v.get().split(" | ")
            s_path = os.path.join(self.prod_dir, f"{s_bid}_{s_m.lower().replace(' ','_')}.js")
            d_path = os.path.join(self.prod_dir, f"{d_bid}_{d_m.lower().replace(' ','_')}.js")
            s_data = self.read_js(s_path); d_data = self.read_js(d_path)
            existing_arts = [p['art'] for p in d_data]; count = 0
            for p in s_data:
                if p['art'] not in existing_arts: d_data.append(p); count += 1
            var_name = f"PRODUCTS_{d_bid.upper()}_{d_m.upper().replace(' ','_')}"
            self.write_js(d_path, var_name, d_data)
            messagebox.showinfo("ОК", f"Скопировано {count} товаров"); win.destroy()
        ctk.CTkButton(win, text="НАЧАТЬ КОПИРОВАНИЕ", fg_color="green", command=run).pack(pady=20)

    def render_settings_tab(self):
        for widget in self.tab_settings.winfo_children(): widget.destroy()
        conf = self.read_js(self.files["config"])
        if not conf: conf = {"tel": "+7", "addr": "", "tg": "Chevrolete01", "parallax": 0.3, "chatId": "5962134875", "itemsInRow": 4, "itemsPerPage": 20}
        
        # Сетка для основных полей
        ctk.CTkLabel(self.tab_settings, text="📞 Контактная информация", font=("Arial", 14, "bold")).pack(pady=5)
        t_en = ctk.CTkEntry(self.tab_settings, width=350); t_en.insert(0, conf.get('tel', '')); t_en.pack(pady=2)
        a_en = ctk.CTkEntry(self.tab_settings, width=350); a_en.insert(0, conf.get('addr', '')); a_en.pack(pady=2)
        g_en = ctk.CTkEntry(self.tab_settings, width=350); g_en.insert(0, conf.get('tg', '')); g_en.pack(pady=2)
        
        # Настройки сетки (Стрелочки)
        ctk.CTkLabel(self.tab_settings, text="📐 Настройка сетки карточек", font=("Arial", 14, "bold")).pack(pady=15)
        
        def create_stepper(parent, label, start_val):
            frame = ctk.CTkFrame(parent, fg_color="transparent")
            frame.pack(pady=5)
            ctk.CTkLabel(frame, text=label, width=200, anchor="e").pack(side="left", padx=10)
            var = ctk.IntVar(value=start_val)
            ctk.CTkButton(frame, text="<", width=30, command=lambda: var.set(max(1, var.get()-1))).pack(side="left")
            ctk.CTkLabel(frame, textvariable=var, width=40).pack(side="left")
            ctk.CTkButton(frame, text=">", width=30, command=lambda: var.set(var.get()+1)).pack(side="left")
            return var

        row_var = create_stepper(self.tab_settings, "Карточек в ряду:", conf.get('itemsInRow', 4))
        page_var = create_stepper(self.tab_settings, "Всего на странице:", conf.get('itemsPerPage', 20))

        ctk.CTkLabel(self.tab_settings, text="🤖 Telegram Chat ID").pack(pady=(15,0))
        cid_en = ctk.CTkEntry(self.tab_settings, width=350); cid_en.insert(0, conf.get('chatId', '')); cid_en.pack(pady=2)
        
        p_val = ctk.DoubleVar(value=conf.get('parallax', 0.3))
        ctk.CTkLabel(self.tab_settings, text="Эффект параллакса").pack()
        ctk.CTkSlider(self.tab_settings, from_=0, to=1, variable=p_val, width=350).pack(pady=5)

        def save_conf():
            new_conf = {
                "tel": t_en.get(), "addr": a_en.get(), "tg": g_en.get(), 
                "parallax": p_val.get(), "chatId": cid_en.get(),
                "itemsInRow": row_var.get(), "itemsPerPage": page_var.get()
            }
            self.write_js(self.files["config"], "SITE_CONFIG", new_conf)
            messagebox.showinfo("ОК", "Настройки сайта сохранены!")
        
        ctk.CTkButton(self.tab_settings, text="💾 СОХРАНИТЬ ВСЁ", height=45, fg_color="#2980b9", command=save_conf).pack(pady=30)

    # --- Методы добавления (без изменений) ---
    def add_brand_win(self):
        name = ctk.CTkInputDialog(text="Название марки:", title="Марка").get_input()
        if name:
            data = self.read_js(self.files["brands"])
            bid = name.lower().replace(" ", "")
            data.append({"id": bid, "name": name.upper(), "img": "default.jpg"})
            self.write_js(self.files["brands"], "BRANDS_DATA", data)

    def add_model_win(self):
        brands = self.read_js(self.files["brands"])
        if not brands: return
        win = ctk.CTkToplevel(self); win.geometry("300x250"); win.attributes("-topmost", True)
        b_names = [b['name'] for b in brands]; b_var = ctk.StringVar(value=b_names[0])
        ctk.CTkOptionMenu(win, values=b_names, variable=b_var).pack(pady=10)
        en = ctk.CTkEntry(win, placeholder_text="Модель"); en.pack(pady=10)
        def save():
            models = self.read_js(self.files["models"])
            bid = next(b['id'] for b in brands if b['name'] == b_var.get())
            if bid not in models: models[bid] = []
            models[bid].append({"name": en.get(), "img": "default.jpg"})
            self.write_js(self.files["models"], "MODELS_DATA", models); win.destroy()
        ctk.CTkButton(win, text="ОК", command=save).pack()

    def add_kat_win(self):
        models_dict = self.read_js(self.files["models"])
        all_m = [m['name'] for bid in models_dict for m in models_dict[bid]]
        if not all_m: return
        win = ctk.CTkToplevel(self); win.geometry("300x250"); win.attributes("-topmost", True)
        m_var = ctk.StringVar(value=all_m[0]); ctk.CTkOptionMenu(win, values=all_m, variable=m_var).pack(pady=10)
        en = ctk.CTkEntry(win, placeholder_text="Тип"); en.pack(pady=10)
        def save():
            kats = self.read_js(self.files["kat"])
            if m_var.get() not in kats: kats[m_var.get()] = ["Все"]
            kats[m_var.get()].append(en.get()); self.write_js(self.files["kat"], "CATEGORIES_DATA", kats); win.destroy()
        ctk.CTkButton(win, text="ОК", command=save).pack()

    def copy_categories_win(self):
        kats = self.read_js(self.files["kat"])
        models_list = list(kats.keys())
        if not models_list: return
        win = ctk.CTkToplevel(self); win.geometry("400x400"); win.attributes("-topmost", True)
        ctk.CTkLabel(win, text="Донор (Откуда):").pack()
        src_var = ctk.StringVar(value=models_list[0]); ctk.CTkOptionMenu(win, values=models_list, variable=src_var).pack(pady=5)
        ctk.CTkLabel(win, text="Цель (Куда):").pack()
        models_dict = self.read_js(self.files["models"])
        target_models = [m['name'] for bid in models_dict for m in models_dict[bid]]
        dst_var = ctk.StringVar(value=target_models[0]); ctk.CTkOptionMenu(win, values=target_models, variable=dst_var).pack(pady=5)
        def do_copy():
            kats[dst_var.get()] = list(set(kats.get(src_var.get(), ["Все"])))
            self.write_js(self.files["kat"], "CATEGORIES_DATA", kats); win.destroy(); messagebox.showinfo("ОК", "Готово")
        ctk.CTkButton(win, text="СКОПИРОВАТЬ", command=do_copy).pack(pady=20)

    def add_part_win(self):
        brands = self.read_js(self.files["brands"])
        models_dict = self.read_js(self.files["models"])
        kats_dict = self.read_js(self.files["kat"])
        if not brands: return
        win = ctk.CTkToplevel(self); win.geometry("500x900"); win.attributes("-topmost", True)
        self.temp_images = []
        b_var = ctk.StringVar(value=brands[0]['name']); ctk.CTkOptionMenu(win, values=[b['name'] for b in brands], variable=b_var).pack(pady=5)
        m_var = ctk.StringVar(); m_menu = ctk.CTkOptionMenu(win, variable=m_var); m_menu.pack(pady=5)
        def up_m(*a):
            bid = next(b['id'] for b in brands if b['name'] == b_var.get())
            ms = [m['name'] for m in models_dict.get(bid, [])]
            m_menu.configure(values=ms); m_var.set(ms[0] if ms else "")
        b_var.trace("w", up_m); up_m()
        t_var = ctk.StringVar(); t_menu = ctk.CTkOptionMenu(win, variable=t_var); t_menu.pack(pady=5)
        def up_k(*a):
            ks = kats_dict.get(m_var.get(), ["Все"]); t_menu.configure(values=ks); t_var.set(ks[0])
        m_var.trace("w", up_k); up_k()
        n_en = ctk.CTkEntry(win, placeholder_text="Бренд"); n_en.pack(pady=5, fill="x", padx=30)
        a_en = ctk.CTkEntry(win, placeholder_text="Артикул"); a_en.pack(pady=5, fill="x", padx=30)
        p_en = ctk.CTkEntry(win, placeholder_text="Цена"); p_en.pack(pady=5, fill="x", padx=30)
        desc_text = ctk.CTkTextbox(win, height=100); desc_text.pack(pady=5, fill="x", padx=30)
        lbl = ctk.CTkLabel(win, text="Фото: 0"); lbl.pack()
        def pick():
            fs = filedialog.askopenfilenames()
            if fs: self.temp_images = list(fs); lbl.configure(text=f"Фото: {len(fs)}")
        ctk.CTkButton(win, text="🖼️ Выбрать фото", command=pick).pack()
        def save():
            art = a_en.get().strip(); imgs = []
            for i, p in enumerate(self.temp_images):
                name = f"{re.sub(r'[^a-zA-Z0-9]', '_', art)}_{i}.jpg"
                shutil.copy(p, os.path.join(self.img_dir, name)); imgs.append(name)
            bid = next(b['id'] for b in brands if b['name'] == b_var.get())
            mid = m_var.get().strip().lower().replace(" ", "_")
            path = os.path.join(self.prod_dir, f"{bid}_{mid}.js")
            data = self.read_js(path)
            data.append({"type": t_var.get(), "brand": n_en.get(), "art": art, "price": int(p_en.get() or 0), "desc": desc_text.get("1.0","end-1c").strip(), "images": imgs, "stock": True})
            self.write_js(path, f"PRODUCTS_{bid.upper()}_{mid.upper()}", data); win.destroy()
        ctk.CTkButton(win, text="СОХРАНИТЬ", fg_color="green", command=save).pack(pady=20)

    # --- Новые функции удаления ---
    def del_brand_win(self):
        brands = self.read_js(self.files["brands"])
        if not brands: return
        names = [b['name'] for b in brands]
        win = ctk.CTkToplevel(self); win.title("Удаление марки"); win.attributes("-topmost", True)
        var = ctk.StringVar(value=names[0]); ctk.CTkOptionMenu(win, values=names, variable=var).pack(pady=20)
        def confirm():
            new_data = [b for b in brands if b['name'] != var.get()]
            self.write_js(self.files["brands"], "BRANDS_DATA", new_data)
            win.destroy(); messagebox.showinfo("ОК", "Марка удалена")
        ctk.CTkButton(win, text="ПОДТВЕРДИТЬ УДАЛЕНИЕ", fg_color="red", command=confirm).pack(pady=10)

    def del_model_win(self):
        models_dict = self.read_js(self.files["models"])
        all_m = []
        for bid in models_dict:
            for m in models_dict[bid]: all_m.append(f"{bid} | {m['name']}")
        if not all_m: return
        win = ctk.CTkToplevel(self); win.title("Удаление модели"); win.attributes("-topmost", True)
        var = ctk.StringVar(value=all_m[0]); ctk.CTkOptionMenu(win, values=all_m, variable=var).pack(pady=20)
        def confirm():
            bid_sel, mname_sel = var.get().split(" | ")
            models_dict[bid_sel] = [m for m in models_dict[bid_sel] if m['name'] != mname_sel]
            self.write_js(self.files["models"], "MODELS_DATA", models_dict)
            win.destroy(); messagebox.showinfo("ОК", "Модель удалена")
        ctk.CTkButton(win, text="УДАЛИТЬ", fg_color="red", command=confirm).pack(pady=10)

    def del_kat_win(self):
        kats = self.read_js(self.files["kat"])
        models = list(kats.keys())
        if not models: return
        win = ctk.CTkToplevel(self); win.title("Удаление типа"); win.attributes("-topmost", True)
        m_var = ctk.StringVar(value=models[0]); m_menu = ctk.CTkOptionMenu(win, values=models, variable=m_var); m_menu.pack(pady=10)
        t_var = ctk.StringVar(); t_menu = ctk.CTkOptionMenu(win, variable=t_var); t_menu.pack(pady=10)
        def up_t(*a):
            ts = kats.get(m_var.get(), [])
            t_menu.configure(values=ts); t_var.set(ts[0] if ts else "")
        m_var.trace("w", up_t); up_t()
        def confirm():
            if t_var.get() in kats[m_var.get()]:
                kats[m_var.get()].remove(t_var.get())
                self.write_js(self.files["kat"], "CATEGORIES_DATA", kats)
                win.destroy(); messagebox.showinfo("ОК", "Тип удален")
        ctk.CTkButton(win, text="УДАЛИТЬ", fg_color="red", command=confirm).pack(pady=10)

if __name__ == "__main__":
    app = AutoManager(); app.mainloop()