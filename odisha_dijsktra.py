import tkinter as tk
from tkinter import ttk, messagebox
import math

# Basic Odisha locations with coordinates (for canvas visualization)
places = [
    "Bhubaneswar", "Cuttack", "Puri", "Konark", "Rourkela", "Sambalpur", "Berhampur",
    "Balasore", "Jeypore", "Baripada", "Angul", "Koraput", "Rayagada", "Keonjhar",
    "Jharsuguda", "Bhawanipatna", "Paradip", "Nayagarh", "Sundargarh", "Jagatsinghpur"
]

# Sample coordinates for visualization (x, y; to position nodes on the canvas)
coords = {
    "Bhubaneswar": (400, 220),
    "Cuttack": (430, 150),
    "Puri": (370, 320),
    "Konark": (480, 290),
    "Rourkela": (80, 60),
    "Sambalpur": (180, 130),
    "Berhampur": (250, 420),
    "Balasore": (570, 80),
    "Jeypore": (120, 380),
    "Baripada": (600, 120),
    "Angul": (280, 180),
    "Koraput": (90, 320),
    "Rayagada": (170, 290),
    "Keonjhar": (440, 80),
    "Jharsuguda": (120, 90),
    "Bhawanipatna": (100, 240),
    "Paradip": (570, 210),
    "Nayagarh": (340, 250),
    "Sundargarh": (60, 120),
    "Jagatsinghpur": (525, 170)
}

# The graph: adjacency list with distances (simplified)
graph = {
    "Bhubaneswar": {"Cuttack":30, "Puri":60, "Konark":65, "Nayagarh":90, "Jagatsinghpur":55, "Paradip":95},
    "Cuttack": {"Bhubaneswar":30, "Angul":110, "Jagatsinghpur":45, "Keonjhar":150},
    "Puri": {"Bhubaneswar":60, "Konark":40, "Berhampur":160},
    "Konark": {"Puri":40, "Bhubaneswar":65},
    "Rourkela": {"Sambalpur":160, "Jharsuguda":110, "Sundargarh":60},
    "Sambalpur": {"Rourkela":160, "Jharsuguda":80, "Angul":150, "Bhawanipatna":170},
    "Berhampur": {"Rayagada":160, "Puri":160},
    "Balasore": {"Baripada":70, "Keonjhar":180},
    "Jeypore": {"Koraput":80, "Rayagada":130},
    "Baripada": {"Balasore":70, "Keonjhar":100},
    "Angul": {"Cuttack":110, "Sambalpur":150, "Keonjhar":190},
    "Koraput": {"Jeypore":80, "Rayagada":120},
    "Rayagada": {"Koraput":120, "Berhampur":160, "Bhawanipatna":175},
    "Keonjhar": {"Cuttack":150, "Baripada":100, "Angul":190, "Balasore":180},
    "Jharsuguda": {"Rourkela":110, "Sambalpur":80, "Sundargarh":75},
    "Bhawanipatna": {"Sambalpur":170, "Rayagada":175},
    "Paradip": {"Bhubaneswar":95, "Jagatsinghpur":45},
    "Nayagarh": {"Bhubaneswar":90},
    "Sundargarh": {"Rourkela":60, "Jharsuguda":75},
    "Jagatsinghpur": {"Cuttack":45, "Paradip":45, "Bhubaneswar":55},
}

# Tkinter colors
NODE_COLOR = "#000000"  # Dark black color
NODE_RADIUS = 20
EDGE_COLOR = "#8E9196"
PATH_EDGE_COLOR = "#0FA0CE"
PATH_NODE_COLOR = "#0FA0CE"
VISITED_NODE_COLOR = "#9b87f5"

class DijkstraVisualizer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Odisha Shortest Path Visualizer - Dijkstra Algorithm")
        self.geometry("1000x800")
        self.resizable(False, False)

        self.canvas = tk.Canvas(self, bg="#E5DEFF", width=650, height=550)
        self.canvas.grid(row=0, column=0, rowspan=8, padx=(20, 10), pady=20, sticky='nsew')

        # Controls
        ttk.Label(self, text="Start:", font=("Arial", 12)).grid(row=0, column=1, sticky="w", padx=(5, 0), pady=(30, 0))
        self.start_var = tk.StringVar(value=places[0])
        self.start_menu = ttk.Combobox(self, textvariable=self.start_var, values=places, state="readonly", width=18)
        self.start_menu.grid(row=0, column=2, sticky="w", padx=(0, 20), pady=(30, 0))

        ttk.Label(self, text="End:", font=("Arial", 12)).grid(row=1, column=1, sticky="w", padx=(5, 0))
        self.end_var = tk.StringVar(value=places[1])
        self.end_menu = ttk.Combobox(self, textvariable=self.end_var, values=places, state="readonly", width=18)
        self.end_menu.grid(row=1, column=2, sticky="w", padx=(0, 20))

        self.step_text = tk.Text(self, width=45, height=20, font=("Consolas", 10), bg="#fff", fg="#333333", borderwidth=2, relief="sunken")
        self.step_text.grid(row=2, column=1, columnspan=2, rowspan=4, padx=5, pady=(8,0), sticky='n')

        run_btn = tk.Button(self, text="Find Shortest Path", font=("Arial", 13, "bold"), bg="#9b87f5", fg="white", relief="raised", command=self.run_dijkstra)
        run_btn.grid(row=6, column=1, columnspan=2, sticky="ew", pady=(15, 5), padx=5, ipadx=5, ipady=9)

        self.reset_btn = tk.Button(self, text="Reset", font=("Arial", 13), bg="#E5DEFF", fg="#7E69AB", relief="groove", command=self.reset, borderwidth=2)
        self.reset_btn.grid(row=7, column=1, columnspan=2, sticky="ew", pady=2, padx=5, ipadx=5, ipady=4)

        self.nodes_drawn = {}
        self.last_path = []
        self.draw_graph()

    def draw_graph(self, highlight_path=None, visited=None):
        self.canvas.delete("all")
        self.nodes_drawn.clear()
        for u, neighbors in graph.items():
            x1, y1 = coords[u]
            for v, dist in neighbors.items():
                x2, y2 = coords[v]
                color = EDGE_COLOR
                width = 2
                if highlight_path and ((u, v) in highlight_path or (v, u) in highlight_path):
                    color = PATH_EDGE_COLOR
                    width = 4
                self.canvas.create_line(x1, y1, x2, y2, fill=color, width=width)
        for place, (x, y) in coords.items():
            fill = NODE_COLOR
            outline = "#1A1F2C"
            width = 2
            if visited and place in visited:
                fill = VISITED_NODE_COLOR
                width = 3
            if highlight_path and place in [n for uv in highlight_path for n in uv]:
                fill = PATH_NODE_COLOR
                width = 4
            oval = self.canvas.create_oval(x - NODE_RADIUS, y - NODE_RADIUS, x + NODE_RADIUS, y + NODE_RADIUS, fill=fill, outline=outline, width=width)
            # Display the full name of the place
            text = self.canvas.create_text(x, y, text=place, font=("Arial", 10, "bold"), fill="white")
            self.nodes_drawn[place] = oval

    def run_dijkstra(self):
        start, end = self.start_var.get(), self.end_var.get()
        if start == end:
            messagebox.showinfo("Invalid", "Source and destination must be different.")
            return
        self.step_text.delete(1.0, tk.END)
        # Dijkstra Initialization
        distances = {node: math.inf for node in places}
        previous = {node: None for node in places}
        visited = set()
        steps = []

        distances[start] = 0
        unvisited = set(places)

        while unvisited:
            curr = min((node for node in unvisited), key=lambda n: distances[n])
            if distances[curr] == math.inf:
                break
            visited.add(curr)
            unvisited.remove(curr)

            # Step record
            step_info = f"Visit: {curr}\n"
            for neighbor, weight in graph.get(curr, {}).items():
                if neighbor in unvisited:
                    alt = distances[curr] + weight
                    if alt < distances[neighbor]:
                        step_info += f"  {neighbor}: update dist {distances[neighbor]} → {alt} via {curr}\n"
                        distances[neighbor] = alt
                        previous[neighbor] = curr
                    else:
                        step_info += f"  {neighbor}: skip, current dist {distances[neighbor]}\n"
            self.step_text.insert(tk.END, step_info + "\n")
            self.update()
            # Visualization: show visited after each step
            self.draw_graph(highlight_path=None, visited=visited)
            self.after(250)

        # Get path
        path = []
        node = end
        while node and previous[node] is not None:
            path.append((previous[node], node))
            node = previous[node]
        if not path:
            self.step_text.insert(tk.END, "\nNo path found.\n", "error")
            return
        path = path[::-1]
        # Show final path
        self.draw_graph(highlight_path=path, visited=visited)
        # Print path and distance
        path_node_list = [start]
        for u, v in path:
            path_node_list.append(v)
        out = f"\nShortest path: {' → '.join(path_node_list)}\nDistance: {distances[end]}\n"
        self.step_text.insert(tk.END, out)
        self.last_path = path

    def reset(self):
        self.step_text.delete(1.0, tk.END)
        self.draw_graph()
        self.last_path = []

if __name__ == "__main__":
    DijkstraVisualizer().mainloop()
