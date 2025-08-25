import tkinter as tk
from tkinter import ttk, messagebox
from math import cos, sin, radians


class DHCalculator:
    def __init__(self, root):
        self.root = root
        self.setup_ui()

    def setup_ui(self):
        self.root.title("Calculator Matrice DH - Robotică")
        self.root.geometry("1920x1080")
        self.root.configure(bg="#f5f5f5")

        style = ttk.Style()
        style.configure('TFrame', background="#f5f5f5")
        style.configure('TLabel', background="#f5f5f5", font=('Arial', 16, 'bold'), foreground="#333")
        style.configure('TButton', font=('Arial', 14, 'bold'), padding=10, background="#4CAF50", foreground="white")
        style.map('TButton', background=[('active', '#45a049')])
        style.configure('TTreeview', font=('Arial', 14), background="#f9f5f5", foreground="#333", rowheight=40)
        style.configure('TTreeview.Heading', font=('Arial', 16, 'bold'), background="#4CAF50", foreground="white")

        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        left_panel = ttk.Frame(main_frame, width=400, relief="solid", borderwidth=2)
        left_panel.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")

        right_panel = ttk.Frame(main_frame, relief="solid", borderwidth=2)
        right_panel.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")

        main_frame.grid_columnconfigure(1, weight=1)
        left_panel.grid_propagate(False)
        right_panel.grid_propagate(False)

        ttk.Label(left_panel, text="Parametrii Denavit-Hartenberg", style='TLabel').pack(pady=10)

        columns = ("Articulație", "θ (°)", "d (mm)", "r (mm)", "α (°)")
        self.dh_tree = ttk.Treeview(left_panel, columns=columns, show="headings", height=6)

        col_widths = [100, 80, 80, 80, 80]
        for col, width in zip(columns, col_widths):
            self.dh_tree.heading(col, text=col)
            self.dh_tree.column(col, width=width, anchor="center")

        self.default_values = [
            ("Axa1", 0.0, 630.0, 600.0, 90.0),
            ("Axa2", -90.0, 0.0, 1280.0, 0.0),
            ("Axa3", 0.0, 0.0, 200.0, -90.0),
            ("Axa4", 0.0, 1142.0, 0.0, 90.0),
            ("Axa5", 0.0, 0.0, 0.0, -90.0),
            ("Axa6", 90.0, 200.0, 0.0, 0.0)
        ]
        self.reset_table()

        self.dh_tree.pack(pady=10, padx=10, fill="both", expand=True)
        self.dh_tree.bind("<Double-1>", self.on_double_click)

        ttk.Button(left_panel, text="Calculează Matricele", command=self.calculate_dh, style='TButton').pack(pady=10, ipadx=10, ipady=5)
        ttk.Button(left_panel, text="Resetează Tabelul", command=self.reset_table, style='TButton').pack(pady=5, ipadx=10, ipady=5)
        ttk.Button(left_panel, text="Exportă Rezultate", command=self.export_results, style='TButton').pack(pady=5, ipadx=10, ipady=5)

        self.results_label = ttk.Label(right_panel, text="Rezultate Transformări", style='TLabel')
        self.results_label.pack(pady=10)

        self.results_canvas = tk.Canvas(right_panel, bg="#f5f5f5", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(right_panel, orient="vertical", command=self.results_canvas.yview)
        self.results_frame = ttk.Frame(self.results_canvas)

        self.results_frame.bind("<Configure>", lambda e: self.results_canvas.configure(scrollregion=self.results_canvas.bbox("all")))

        self.results_canvas.create_window((0, 0), window=self.results_frame, anchor="nw")
        self.results_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.results_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def reset_table(self):
        for item in self.dh_tree.get_children():
            self.dh_tree.delete(item)
        for values in self.default_values:
            self.dh_tree.insert("", "end", values=values)

    def on_double_click(self, event):
        item = self.dh_tree.identify_row(event.y)
        column = self.dh_tree.identify_column(event.x)
        if not item or not column:
            return
        col_index = int(column.replace('#', '')) - 1
        x, y, width, height = self.dh_tree.bbox(item, column)
        value = self.dh_tree.set(item, column)

        entry = tk.Entry(self.dh_tree)
        entry.place(x=x, y=y, width=width, height=height)
        entry.insert(0, value)
        entry.focus()

        def save_edit(event):
            new_value = entry.get()
            self.dh_tree.set(item, column, new_value)
            entry.destroy()

        entry.bind('<Return>', save_edit)
        entry.bind('<FocusOut>', lambda e: entry.destroy())

    def format_matrix(self, matrix):
        formatted_matrix = []
        for row in matrix:
            formatted_row = []
            for val in row:
                if isinstance(val, float) and val == 0.0:
                    formatted_row.append('0')
                elif isinstance(val, float) and val.is_integer():
                    formatted_row.append(str(int(val)))
                else:
                    formatted_row.append(str(val))
            formatted_matrix.append(formatted_row)
        return formatted_matrix

    def multiply_matrices(self, A, B):
        return [[sum(A[i][k] * B[k][j] for k in range(4)) for j in range(4)] for i in range(4)]

    def create_matrix_table(self, parent, matrix, title):
        frame = ttk.Frame(parent, borderwidth=2, relief="groove", padding=10)
        ttk.Label(frame, text=title, font=('Arial', 10, 'bold')).pack(pady=(0, 5))

        tree = ttk.Treeview(frame, height=4, show="headings")
        tree["columns"] = ("1", "2", "3", "4")

        for col in tree["columns"]:
            tree.column(col, width=80, anchor="center")
            tree.heading(col, text=col)

        for row in matrix:
            tree.insert("", "end", values=row)

        tree.pack()
        return frame

    def calculate_dh(self):
        try:
            for widget in self.results_frame.winfo_children():
                widget.destroy()

            params = []
            for child in self.dh_tree.get_children():
                values = self.dh_tree.item(child)['values']
                try:
                    params.append(tuple(float(x) if i > 0 else x for i, x in enumerate(values)))
                except ValueError:
                    messagebox.showerror("Eroare", "Parametrii invalizi. Verificați valorile.")
                    return

            matrices = []
            for i, (joint, theta, d, a, alpha) in enumerate(params):
                A = [
                    [round(cos(radians(theta)), 2),
                     round(-sin(radians(theta)) * cos(radians(alpha)), 2),
                     round(sin(radians(theta)) * sin(radians(alpha)), 2),
                     round(a * cos(radians(theta)), 2)],
                    [round(sin(radians(theta)), 2),
                     round(cos(radians(theta)) * cos(radians(alpha)), 2),
                     round(-cos(radians(theta)) * sin(radians(alpha)), 2),
                     round(a * sin(radians(theta)), 2)],
                    [0,
                     round(sin(radians(alpha)), 2),
                     round(cos(radians(alpha)), 2),
                     round(d, 2)],
                    [0, 0, 0, 1]
                ]
                matrices.append(A)

                frame = self.create_matrix_table(self.results_frame, self.format_matrix(A), f"Matricea A{i + 1} (Articulația {joint})")
                frame.pack(pady=5, fill="x")

            if not matrices:
                return

            T = matrices[0]
            frame = self.create_matrix_table(self.results_frame, self.format_matrix(T), "T1 = A01")
            frame.pack(pady=10, fill="x")

            for i in range(1, len(matrices)):
                T = self.multiply_matrices(T, matrices[i])
                frame = self.create_matrix_table(self.results_frame, self.format_matrix(T), f"Rezultat T{i + 1}*A{i + 1}")
                frame.pack(pady=10, fill="x")

            final_frame = ttk.LabelFrame(self.results_frame, text="Matrice Finală T", padding=10)
            final_matrix_table = self.create_matrix_table(final_frame, self.format_matrix(T), "T Final")
            final_matrix_table.pack()
            final_frame.pack(pady=20, fill="x")

        except Exception as e:
            messagebox.showerror("Eroare", f"Eroare la calcul: {str(e)}")

    def export_results(self):
        try:
            with open("rezultate_dh.txt", "w") as f:
                for widget in self.results_frame.winfo_children():
                    if isinstance(widget, ttk.Frame):
                        children = widget.winfo_children()
                        if len(children) >= 2:
                            title = children[0]['text']
                            f.write(f"{title}:\n")
                            tree = children[1]
                            for child in tree.get_children():
                                values = tree.item(child)['values']
                                f.write("  " + "\t".join(map(str, values)) + "\n")
                            f.write("\n")
            messagebox.showinfo("Export", "Rezultatele au fost salvate în 'rezultate_dh.txt'")
        except Exception as e:
            messagebox.showerror("Eroare", f"Nu s-a putut salva fișierul: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = DHCalculator(root)
    root.mainloop()
