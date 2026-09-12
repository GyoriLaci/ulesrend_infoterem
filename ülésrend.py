import os
import random
import tempfile
import tkinter as tk
import webbrowser
from tkinter import filedialog, messagebox


class ClassroomSeatingApp:

    def __init__(self, root):
        self.root = root
        self.root.title("101-es terem ülésrend generátor")
        self.root.resizable(False, False)

        # Classroom layout: True indicates a desk exists
        self.left_layout = [[True] * 4 for _ in range(4)]
        self.right_layout = [
            [True, True, True, True],
            [True, True, True, True],
            [True, True, True, True],
            [True, True, False, False],
        ]

        self.students = []
        self.desks = {}

        self._build_controls()
        self._build_classroom()

    def _build_controls(self):
        control_frame = tk.Frame(self.root, pady=12, padx=10)
        control_frame.pack(fill="x")

        load_btn = tk.Button(
            control_frame,
            text="📁 Nevek betöltése (.txt)",
            command=self.load_names_file,
            font=("Segoe UI", 9, "bold"),
            padx=8,
        )
        load_btn.pack(side="left", padx=5)

        self.status_label = tk.Label(
            control_frame,
            text="Nincs betöltött névlista",
            font=("Segoe UI", 9, "italic"),
            fg="#555",
        )
        self.status_label.pack(side="left", padx=5)

        gen_btn = tk.Button(
            control_frame,
            text="Ülésrend generálása",
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
            text="Ülésrend visszaállítása",
            command=self.reset_all,
            font=("Segoe UI", 9),
            padx=8,
        )
        reset_btn.pack(side="left", padx=4)

        info_label = tk.Label(
            control_frame,
            text="• Kattintson az asztalra a HIBÁS/ELÉRHETŐ állapot váltásához",
            font=("Segoe UI", 9, "italic"),
            fg="#555",
        )
        info_label.pack(side="right", padx=10)

    def _build_classroom(self):
        room_frame = tk.Frame(self.root, padx=25, pady=15, bg="#F3F4F6")
        room_frame.pack()

        # Left block
        left_frame = tk.Frame(room_frame, bg="#F3F4F6")
        left_frame.pack(side="left", padx=(0, 40))
        self._populate_grid(left_frame, self.left_layout, prefix="L")

        # Right block
        right_frame = tk.Frame(room_frame, bg="#F3F4F6")
        right_frame.pack(side="left")
        self._populate_grid(right_frame, self.right_layout, prefix="R")

    def _populate_grid(self, parent_frame, layout, prefix):
        for r_idx, row in enumerate(layout):
            for c_idx, exists in enumerate(row):
                if exists:
                    desk_id = f"{prefix}_R{r_idx+1}_C{c_idx+1}"
                    btn = tk.Button(
                        parent_frame,
                        text="Elérhető",
                        width=14,
                        height=3,
                        wraplength=100,
                        bg="#E5E7EB",
                        fg="#1F2937",
                        font=("Segoe UI", 8),
                        relief="solid",
                        bd=1,
                        command=lambda d=desk_id: self.toggle_broken(d),
                    )
                    btn.grid(row=r_idx, column=c_idx, padx=4, pady=8)
                    self.desks[desk_id] = {
                        "btn": btn,
                        "status": "working",
                        "text": "Elérhető",
                    }
                else:
                    spacer = tk.Label(
                        parent_frame, width=14, height=3, bg="#F3F4F6"
                    )
                    spacer.grid(row=r_idx, column=c_idx, padx=4, pady=8)

    def load_names_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f.readlines()]

            parsed_names = []
            i = 0
            while i < len(lines):
                line = lines[i]
                if line.isdigit():
                    if i + 1 < len(lines):
                        name = lines[i + 1].strip()
                        if name and name != "-":
                            parsed_names.append(name)
                        i += 2
                        while i < len(lines) and lines[i] != "-":
                            i += 1
                i += 1

            if not parsed_names:
                messagebox.showwarning(
                    "Warning", "Nem találhatók megfelelő nevek a megadott minta alapján."
                )
                return

            self.students = parsed_names
            self.status_label.config(
                text=f"{len(self.students)} diák betöltve",
                fg="#059669",
                font=("Segoe UI", 9, "bold"),
            )

        except Exception as e:
            messagebox.showerror(
                "Error", f"Nem sikerült a fájlt olvasni:\n{str(e)}"
            )

    def toggle_broken(self, desk_id):
        desk = self.desks[desk_id]
        if desk["status"] == "working":
            desk["status"] = "broken"
            desk["text"] = "HIBÁS"
            desk["btn"].config(bg="#EF4444", fg="white", text="HIBÁS")
        else:
            desk["status"] = "working"
            desk["text"] = "Elérhető"
            desk["btn"].config(bg="#E5E7EB", fg="#1F2937", text="Elérhető")

    def generate_seating(self):
        if not self.students:
            messagebox.showwarning(
                "Missing Data", "Please load a .txt file with students first."
            )
            return

        available_desks = [
            k for k, v in self.desks.items() if v["status"] == "working"
        ]

        if len(self.students) > len(available_desks):
            messagebox.showwarning(
                "Capacity Exceeded",
                f"Ön {len(self.students)} diákot, de csak {len(available_desks)} működő számítógépe van.",
            )
            return

        # Clear active desks
        for desk_id in available_desks:
            self.desks[desk_id]["btn"].config(
                bg="#E5E7EB", fg="#1F2937", text="Üres"
            )
            self.desks[desk_id]["text"] = "Üres"

        # Shuffle and assign
        shuffled_students = self.students.copy()
        random.shuffle(shuffled_students)
        random.shuffle(available_desks)

        for name, desk_id in zip(shuffled_students, available_desks):
            self.desks[desk_id]["btn"].config(
                bg="#BBF7D0", fg="#064E3B", text=name
            )
            self.desks[desk_id]["text"] = name

    def reset_all(self):
        for desk in self.desks.values():
            desk["status"] = "working"
            desk["text"] = "Elérhető"
            desk["btn"].config(bg="#E5E7EB", fg="#1F2937", text="Elérhető")

    def print_seating_chart(self):
        # Generate HTML representation of both sides
        def render_block(layout, prefix):
            html = '<div class="desk-grid">'
            for r in range(4):
                html += '<div class="desk-row">'
                for c in range(4):
                    if layout[r][c]:
                        desk_id = f"{prefix}_R{r+1}_C{c+1}"
                        desk = self.desks[desk_id]
                        status_class = (
                            "broken"
                            if desk["status"] == "broken"
                            else (
                                "occupied"
                                if desk["text"]
                                not in ["Elérhető", "Üres", "HIBÁS"]
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

        left_html = render_block(self.left_layout, "L")
        right_html = render_block(self.right_layout, "R")

        html_content = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>101-es terem ülésrend</title>
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
            <h2>101-es terem ülésrend</h2>
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

        # Save to a temp HTML file and launch the default browser
        temp_file = os.path.join(
            tempfile.gettempdir(), "ültetésirend.html"
        )
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        webbrowser.open(f"file://{os.path.abspath(temp_file)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ClassroomSeatingApp(root)
    root.mainloop()