import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os

class SQLCompilerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SQL Studio - Pro Edition")
        self.root.geometry("1100x850")
        self.root.configure(bg="#1e1e1e")

        # --- MENU BAR ---
        self.menubar = tk.Menu(root)
        self.filemenu = tk.Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="Open SQL File...", command=self.upload_file)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=root.quit)
        self.menubar.add_cascade(label="File", menu=self.filemenu)
        root.config(menu=self.menubar)

        # Main Paned Window
        self.main_pane = tk.PanedWindow(root, orient=tk.VERTICAL, bg="#2d2d2d", sashwidth=6)
        self.main_pane.pack(fill=tk.BOTH, expand=True)

        # --- EDITOR SECTION ---
        self.editor_frame = tk.Frame(self.main_pane, bg="#1e1e1e")
        self.main_pane.add(self.editor_frame, height=500)

        self.line_canvas = tk.Canvas(self.editor_frame, width=50, bg="#1e1e1e", highlightthickness=0)
        self.line_canvas.pack(side=tk.LEFT, fill=tk.Y)

        self.text_area = tk.Text(self.editor_frame, font=("Consolas", 13), bg="#1e1e1e", 
                                 fg="#d4d4d4", insertbackground="white", undo=True, wrap=tk.NONE)
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Config Tags
        self.text_area.tag_configure("error_highlight", foreground="#f44747", underline=True)
        self.text_area.tag_configure("jump_highlight", background="#3e3e3e")

        self.scrollbar = tk.Scrollbar(self.editor_frame, command=self.text_area.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_area.config(yscrollcommand=self.set_scroll)

        # --- PROBLEMS SECTION ---
        self.bottom_frame = tk.Frame(self.main_pane, bg="#1e1e1e")
        self.main_pane.add(self.bottom_frame)

        self.tool_bar = tk.Frame(self.bottom_frame, bg="#252526")
        self.tool_bar.pack(fill=tk.X)
        
        tk.Label(self.tool_bar, text="  PROBLEMS (Click error to jump)", fg="#ffffff", bg="#252526", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, pady=8)

        self.run_btn = tk.Button(self.tool_bar, text="Analyze SQL  ▶ ", command=self.run_analysis, 
                                 bg="#0e639c", fg="white", relief=tk.FLAT, padx=15, cursor="hand2")
        self.run_btn.pack(side=tk.RIGHT, padx=10)

        self.upload_btn = tk.Button(self.tool_bar, text="Upload File 📂", command=self.upload_file, 
                                 bg="#3c3c3c", fg="white", relief=tk.FLAT, padx=10, cursor="hand2")
        self.upload_btn.pack(side=tk.RIGHT, padx=5)

        self.problems_view = tk.Text(self.bottom_frame, font=("Consolas", 11), bg="#1e1e1e", 
                                     fg="#f44747", state=tk.DISABLED, highlightthickness=0, padx=10, pady=10, cursor="hand2")
        self.problems_view.pack(fill=tk.BOTH, expand=True)

        # Bindings
        self.text_area.bind("<KeyRelease>", self.update_ui)
        self.text_area.bind("<MouseWheel>", self.update_ui)
        self.problems_view.bind("<ButtonRelease-1>", self.on_problem_click)

    def on_problem_click(self, event):
        """Click handling for problems window."""
        try:
            index = self.problems_view.index(f"@{event.x},{event.y}")
            line_content = self.problems_view.get(f"{index} linestart", f"{index} lineend")
            
            if "Line" in line_content:
                parts = line_content.split(':')
                line_str = parts[0].replace("✖ Line ", "").strip()
                self.jump_to_line(int(line_str))
        except: pass

    def jump_to_line(self, line_num):
        """Scroll and visual highlight."""
        self.text_area.tag_remove("jump_highlight", "1.0", tk.END)
        target_index = f"{line_num}.0"
        self.text_area.see(target_index)
        self.text_area.mark_set("insert", target_index)
        self.text_area.focus_set()
        self.text_area.tag_add("jump_highlight", f"{line_num}.0", f"{line_num}.end")

    def upload_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("SQL Files", "*.sql"), ("Text Files", "*.txt")])
        if file_path:
            with open(file_path, 'r') as f:
                content = f.read()
                self.text_area.delete("1.0", tk.END)
                self.text_area.insert("1.0", content)
            self.update_ui()

    def set_scroll(self, *args):
        self.scrollbar.set(*args)
        self.redraw_line_numbers()

    def update_ui(self, event=None):
        self.redraw_line_numbers()

    def redraw_line_numbers(self):
        self.line_canvas.delete("all")
        i = self.text_area.index("@0,0")
        while True:
            dline = self.text_area.dlineinfo(i)
            if dline is None: break
            y = dline[1]
            linenum = str(i).split(".")[0]
            self.line_canvas.create_text(40, y, anchor="ne", text=linenum, fill="#858585", font=("Consolas", 11))
            i = self.text_area.index("%s+1line" % i)

    def highlight_error(self, line_num, token):
        if not token or token in ["", "(null)", ";"]: return
        start_line = f"{line_num}.0"
        end_line = f"{line_num}.end"
        idx = self.text_area.search(token, start_line, stopindex=end_line, nocase=True)
        if idx:
            end_idx = f"{idx} + {len(token)}c"
            self.text_area.tag_add("error_highlight", idx, end_idx)
        else:
            self.text_area.tag_add("error_highlight", start_line, end_line)

    def run_analysis(self):
        self.text_area.tag_remove("error_highlight", "1.0", tk.END)
        self.text_area.tag_remove("jump_highlight", "1.0", tk.END)
        self.problems_view.config(state=tk.NORMAL)
        self.problems_view.delete("1.0", tk.END)
        
        query = self.text_area.get("1.0", tk.END)
        try:
            result = subprocess.run(["./sql_checker"], input=query, text=True, capture_output=True, encoding="utf-8")
            errors = result.stderr.strip().split('\n')
            found_errors = False
            for line in errors:
                if line.startswith("[ERROR]"):
                    found_errors = True
                    parts = line.split('|')
                    if len(parts) >= 4:
                        self.problems_view.insert(tk.END, f"✖ Line {parts[1]}: {parts[2]} (found '{parts[3]}')\n")
                        self.highlight_error(parts[1], parts[3])
            if not found_errors:
                self.problems_view.insert(tk.END, "✔ No syntax errors found.")
        except Exception as e:
            self.problems_view.insert(tk.END, f"CRITICAL ERROR: {str(e)}")
        
        self.problems_view.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = SQLCompilerApp(root)
    root.update()
    app.redraw_line_numbers()
    root.mainloop()
