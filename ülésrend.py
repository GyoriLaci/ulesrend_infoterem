import os
import random
import tempfile
import tkinter as tk
import webbrowser
from tkinter import filedialog, messagebox


class ClassroomSeatingApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Informatika Terem Ültetésgenerátor")
        self.root.resizable(False, False)

        # Terem elrendezése: True jelöli a létező gépeket
        self.left_layout = [[True] * 4 for _ in range(4)]
        self.right_layout = [
            [True, True, True, True],
            [True, True, True, True],
            [True, True, True, True],
            [True, True, False, False],
        ]

        self.students = []
        self.desks = {}

        # Csere mód állapota
        self.seating_generated = False
        self.selected_desk_for_swap = None

        self._build_controls()
        self._build_classroom()

    def _build_controls(self):
        control_frame = tk.Frame(self.root, pady=12, padx=10)
        control_frame.pack(fill="x")

        load_btn = tk.Button(
            control_frame,
            text="📁 Névsor betöltése (.txt)",
            command=self.load_names_file,
            font=("Segoe UI", 9, "bold"),
            padx=8,
        )
        load_btn.pack(side="left", padx=5)

        self.status_label = tk.Label(
            control_frame,
            text="Nincs fájl betöltve",
            font=("Segoe UI", 9, "italic"),
            fg="#555",
        )
        self.status_label.pack(side="left", padx=5)

        gen_btn = tk.Button(
            control_frame,
            text="Ültetés generálása",
            command=self.generate_seating,
            bg="#2563EB",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            padx=10,
        )
        gen_btn.pack(side="left", padx=8)

        print_btn = tk.Button(
            control_frame,
            text="🖨️ Nyomtatás / PDF",
            command=self.print_seating_chart,
            bg="#059669",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            padx=10,
        )
        print_btn.pack(side="left", padx=4)

        reset_btn = tk.Button(
            control_frame,
            text="Alaphelyzet",
            command=self.reset_all,
            font=("Segoe UI", 9),
            padx=8,
        )
        reset_btn.pack(side="left", padx=4)

        self.info_label = tk.Label(
            control_frame,
            text="• Mód: Hibás gépek kijelölése",
            font=("Segoe UI", 9, "bold"),
            fg="#B91C1C",
        )
        self.info_label.pack(side="right", padx=10)

    def _build_classroom(self):
        room_frame = tk.Frame(self.root, padx=25, pady=15, bg="#F3F4F6")
        room_frame.pack()

        # Bal oldali blokk
        left_frame = tk.Frame(room_frame, bg="#F3F4F6")
        left_frame.pack(side="left", padx=(0, 40))
        self._populate_grid(left_frame, self.left_layout, prefix="B")

        # Jobb oldali blokk
        right_frame = tk.Frame(room_frame, bg="#F3F4F6")
        right_frame.pack(side="left")
        self._populate_grid(right_frame, self.right_layout, prefix="J")

    def _populate_grid(self, parent_frame, layout, prefix):
        for r_idx, row in enumerate(layout):
            for c_idx, exists in enumerate(row):
                if exists:
                    desk_id = f"{prefix}_S{r_idx+1}_O{c_idx+1}"
                    btn = tk.Button(
                        parent_frame,
                        text="Szabad",
                        width=14,
                        height=3,
                        wraplength=100,
                        bg="#E5E7EB",
                        fg="#1F2937",
                        font=("Segoe UI", 8),
                        relief="solid",
                        bd=1,
                        command=lambda d=desk_id: self.handle_desk_click(d),
                    )
                    btn.grid(row=r_idx, column=c_idx, padx=4, pady=8)
                    self.desks[desk_id] = {
                        "btn": btn,
                        "status": "working",
                        "text": "Szabad",
                        "row": r_idx + 1,
                        "col": c_idx + 1,
                        "prefix": prefix,
                    }
                else:
                    spacer = tk.Label(
                        parent_frame, width=14, height=3, bg="#F3F4F6"
                    )
                    spacer.grid(row=r_idx, column=c_idx, padx=4, pady=8)

    def load_names_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Szöveges fájlok", "*.txt"), ("Minden fájl", "*.*")]
        )
        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = [
                    line.replace("\xa0", " ").strip() for line in f.readlines()
                ]

            parsed_names = []
            i = 0
            while i < len(lines):
                line = lines[i]

                # Ha a sor nem üres
                if line:
                    # 1. eset: Külön sorban álló sorszám (pl. "2", "3")
                    if line.isdigit():
                        if i + 1 < len(lines):
                            candidate = lines[i + 1].strip()
                            if candidate and not candidate.endswith("-"):
                                parsed_names.append(candidate)
                                i += 2
                    # 2. eset: Nincs előtte sorszám, közvetlenül névvel kezdődik a blokk
                    elif not line.endswith("-") and not any(
                        c.isdigit() for c in line
                    ):
                        parsed_names.append(line)
                        i += 1

                    # Átugorjuk a blokk többi részét a kötőjeles elválasztóig (pl. "• -", "-", "•	-")
                    while i < len(lines) and not lines[i].endswith("-"):
                        i += 1

                i += 1

            if not parsed_names:
                messagebox.showwarning(
                    "Figyelem",
                    "Nem található név a fájlban a megadott formátum alapján.",
                )
                return

            self.students = parsed_names
            self.status_label.config(
                text=f"{len(self.students)} tanuló betöltve",
                fg="#059669",
                font=("Segoe UI", 9, "bold"),
            )

        except Exception as e:
            messagebox.showerror(
                "Hiba", f"Nem sikerült beolvasni a fájlt:\n{str(e)}"
            )

    def handle_desk_click(self, desk_id):
        # 1. Beállítási fázis: Hibás gépek jelölése
        if not self.seating_generated:
            desk = self.desks[desk_id]
            if desk["status"] == "working":
                desk["status"] = "broken"
                desk["text"] = "HIBÁS GÉP"
                desk["btn"].config(
                    bg="#EF4444", fg="white", text="HIBÁS\nGÉP"
                )
            else:
                desk["status"] = "working"
                desk["text"] = "Szabad"
                desk["btn"].config(bg="#E5E7EB", fg="#1F2937", text="Szabad")
            return

        # 2. Csere fázis: Tanulók cseréje
        desk = self.desks[desk_id]
        if desk["status"] == "broken":
            messagebox.showinfo(
                "Nem cserélhető", "Ez a számítógép üzemen kívül van."
            )
            return

        # Első gép kijelölése
        if self.selected_desk_for_swap is None:
            self.selected_desk_for_swap = desk_id
            desk["btn"].config(bg="#FDE047", fg="#78350F")  # Sárga kiemelés
            self.info_label.config(
                text="• Kattints a másik asztalra a cseréhez", fg="#D97706"
            )
        else:
            first_id = self.selected_desk_for_swap
            second_id = desk_id

            # Ha ugyanarra kattintunk, visszavonjuk a kijelölést
            if first_id == second_id:
                self._refresh_desk_display(first_id)
                self.selected_desk_for_swap = None
                self.info_label.config(
                    text="• Mód: Kattints 2 gépre a cseréhez", fg="#2563EB"
                )
                return

            # Helyek felcserélése
            self.desks[first_id]["text"], self.desks[second_id]["text"] = (
                self.desks[second_id]["text"],
                self.desks[first_id]["text"],
            )

            self._refresh_desk_display(first_id)
            self._refresh_desk_display(second_id)

            self.selected_desk_for_swap = None
            self.info_label.config(
                text="• Mód: Kattints 2 gépre a cseréhez", fg="#2563EB"
            )

    def _refresh_desk_display(self, desk_id):
        desk = self.desks[desk_id]
        if desk["status"] == "broken":
            desk["btn"].config(bg="#EF4444", fg="white", text="HIBÁS\nGÉP")
        elif desk["text"] in ["Szabad", "Üres"]:
            desk["btn"].config(bg="#E5E7EB", fg="#1F2937", text="Üres")
        else:
            desk["btn"].config(
                bg="#BBF7D0", fg="#064E3B", text=desk["text"]
            )  # Zöld, kiosztott hely

    def generate_seating(self):
        if not self.students:
            messagebox.showwarning(
                "Hiányzó adatok",
                "Kérlek, először tölts be egy névsort (.txt fájl).",
            )
            return

        working_desks = [
            k for k, v in self.desks.items() if v["status"] == "working"
        ]

        if len(self.students) > len(working_desks):
            messagebox.showwarning(
                "Kapacitás túllépés",
                f"{len(self.students)} tanuló van, de csak {len(working_desks)} működő gép áll rendelkezésre.",
            )
            return

        # Működő helyek rendezése alulról felfelé (4. sortól az 1. felé)
        # Egy soron belül véletlenszerűen keverjük az oszlopokat
        random.shuffle(working_desks)
        working_desks.sort(key=lambda d: self.desks[d]["row"], reverse=True)

        # Működő asztalok kiürítése
        for desk_id in working_desks:
            self.desks[desk_id]["text"] = "Üres"
            self.desks[desk_id]["btn"].config(
                bg="#E5E7EB", fg="#1F2937", text="Üres"
            )

        # Diákok névsorának megkeverése
        shuffled_students = self.students.copy()
        random.shuffle(shuffled_students)

        # Kiosztás alulról felfelé
        for i, name in enumerate(shuffled_students):
            desk_id = working_desks[i]
            self.desks[desk_id]["text"] = name
            self.desks[desk_id]["btn"].config(
                bg="#BBF7D0", fg="#064E3B", text=name
            )

        # Csere mód bekapcsolása
        self.seating_generated = True
        self.selected_desk_for_swap = None
        self.info_label.config(
            text="• Mód: Kattints 2 gépre a cseréhez", fg="#2563EB"
        )

    def reset_all(self):
        self.seating_generated = False
        self.selected_desk_for_swap = None
        for desk in self.desks.values():
            desk["status"] = "working"
            desk["text"] = "Szabad"
            desk["btn"].config(bg="#E5E7EB", fg="#1F2937", text="Szabad")
        self.info_label.config(
            text="• Mód: Hibás gépek kijelölése", fg="#B91C1C"
        )

    def print_seating_chart(self):
        def render_block(layout, prefix):
            html = '<div class="desk-grid">'
            for r in range(4):
                html += '<div class="desk-row">'
                for c in range(4):
                    if layout[r][c]:
                        desk_id = f"{prefix}_S{r+1}_O{c+1}"
                        desk = self.desks[desk_id]
                        status_class = (
                            "broken"
                            if desk["status"] == "broken"
                            else (
                                "occupied"
                                if desk["text"]
                                not in ["Szabad", "Üres", "HIBÁS GÉP"]
                                else "empty"
                            )
                        )
                        text = desk["text"]
                        html += f'<div class="desk {status_class}">{text}</div>'
                    else:
                        html += '<div class="desk spacer"></div>'
                html += "</div>"
            html += "</div>"
            return html

        left_html = render_block(self.left_layout, "B")
        right_html = render_block(self.right_layout, "J")

        html_content = f"""<!DOCTYPE html>
        <html lang="hu">
        <head>
            <meta charset="utf-8">
            <title>Informatika Terem Ülésrend</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    padding: 20px;
                    text-align: center;
                }}
                h2 {{ margin-bottom: 25px; }}
                .room-container {{
                    display: flex;
                    justify-content: center;
                    gap: 60px;
                    margin-top: 10px;
                }}
                .desk-row {{
                    display: flex;
                    gap: 10px;
                    margin-bottom: 12px;
                }}
                .desk {{
                    width: 110px;
                    height: 55px;
                    border: 1.5px solid #333;
                    border-radius: 4px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 11px;
                    font-weight: 600;
                    text-align: center;
                    padding: 2px 4px;
                    box-sizing: border-box;
                    word-break: break-word;
                }}
                .occupied {{ background-color: #e2fbe8; border-color: #15803d; color: #14532d; }}
                .broken {{ background-color: #fee2e2; border-color: #b91c1c; color: #991b1b; }}
                .empty {{ background-color: #f3f4f6; color: #6b7280; }}
                .spacer {{ border: none; background: transparent; }}
                @media print {{
                    body {{ padding: 0; }}
                    @page {{ size: landscape; margin: 15mm; }}
                }}
            </style>
        </head>
        <body>
            <h2>Informatika Terem Ülésrend</h2>
            <div class="room-container">
                {left_html}
                {right_html}
            </div>
            <script>
                window.onload = function() {{
                    window.print();
                }};
            </script>
        </body>
        </html>"""

        temp_file = os.path.join(tempfile.gettempdir(), "ulesrend_nyomtatas.html")
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        webbrowser.open(f"file://{os.path.abspath(temp_file)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ClassroomSeatingApp(root)
    root.mainloop()