"""Smart Bus Reservation - desktop app (Tkinter). Run in IDLE with F5.
Data is kept in memory only: it is lost when the window closes."""
import tkinter as tk
from collections import Counter
from itertools import count
from tkinter import messagebox, ttk

CITIES = ("Karachi", "Hyderabad", "Sukkur", "Mirpur Khas", "Lahore")
routes = {r[0]: {"id": r[0], "from": r[1], "to": r[2], "time": r[3], "price": r[4], "total": r[5], "left": r[5]}
          for r in (("R101", "Karachi", "Hyderabad", "08:00 AM", 1200, 40),
                    ("R102", "Karachi", "Sukkur", "09:30 AM", 2000, 36),
                    ("R103", "Hyderabad", "Mirpur Khas", "11:00 AM", 800, 32),
                    ("R104", "Karachi", "Lahore", "07:00 PM", 5000, 45),
                    ("R105", "Sukkur", "Hyderabad", "02:00 PM", 1500, 30))}
bookings, booking_ids = {}, count(1001)


def pos_int(text):
    """Positive whole number, else None."""
    text = text.strip()
    return int(text) if text.isdecimal() and int(text) > 0 else None


def status(r):
    return "Fully Booked" if not r["left"] else "Available" if r["left"] == r["total"] else "Partially Booked"


def table(parent, columns):
    tree = ttk.Treeview(parent, columns=[c for c, _ in columns], show="headings", height=12)
    for name, width in columns:
        tree.heading(name, text=name)
        tree.column(name, width=width, anchor="w")
    tree.pack(fill="both", expand=True, pady=6)
    return tree


def fill(tree, rows):
    tree.delete(*tree.get_children())
    for row in rows:
        tree.insert("", "end", values=row)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🚌 Smart Bus Reservation")
        self.geometry("860x540")
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=8, pady=8)
        tabs = {n: ttk.Frame(notebook, padding=10) for n in ("Routes", "Search", "Book", "My Bookings", "Report")}
        for name, frame in tabs.items():
            notebook.add(frame, text=name)
        notebook.bind("<<NotebookTabChanged>>", lambda _: self.refresh())

        # Routes tab
        self.only = tk.BooleanVar()
        ttk.Checkbutton(tabs["Routes"], text="Only routes with seats", variable=self.only,
                        command=self.refresh).pack(anchor="w")
        self.routes_tree = table(tabs["Routes"], [("ID", 60), ("Journey", 260), ("Departs", 90),
                                                  ("Fare (Rs.)", 90), ("Seats", 90), ("Status", 130)])
        # Search tab
        self.term = tk.StringVar()
        self.term.trace_add("write", lambda *_: self.refresh())
        ttk.Label(tabs["Search"], text="Route ID or city:").pack(anchor="w")
        ttk.Entry(tabs["Search"], textvariable=self.term, width=40).pack(anchor="w", pady=4)
        self.search_tree = table(tabs["Search"], [("ID", 60), ("Journey", 260), ("Fare (Rs.)", 90), ("Seats free", 90)])
        self.search_note = ttk.Label(tabs["Search"])
        self.search_note.pack(anchor="w")
        # Book tab
        self.name, self.age, self.seats, self.route = (tk.StringVar() for _ in range(4))
        form = tabs["Book"]
        for label, var in (("Passenger name", self.name), ("Age", self.age)):
            ttk.Label(form, text=label).pack(anchor="w")
            ttk.Entry(form, textvariable=var, width=40).pack(anchor="w", pady=4)
        ttk.Label(form, text="Route").pack(anchor="w")
        self.route_box = ttk.Combobox(form, textvariable=self.route, state="readonly", width=50)
        self.route_box.pack(anchor="w", pady=4)
        ttk.Label(form, text="Number of seats").pack(anchor="w")
        ttk.Entry(form, textvariable=self.seats, width=40).pack(anchor="w", pady=4)
        ttk.Button(form, text="Book ticket", command=self.book).pack(anchor="w", pady=10)
        # Bookings tab
        self.book_tree = table(tabs["My Bookings"], [("ID", 70), ("Passenger", 160), ("Route", 70),
                                                     ("Seats", 60), ("Fare (Rs.)", 100), ("Status", 100)])
        ttk.Button(tabs["My Bookings"], text="Cancel selected booking", command=self.cancel).pack(anchor="w")
        # Report tab
        self.report_text = tk.Text(tabs["Report"], height=24, state="disabled", font=("Consolas", 11))
        self.report_text.pack(fill="both", expand=True)
        self.refresh()

    def refresh(self):
        fill(self.routes_tree, [(r["id"], f"{r['from']} -> {r['to']}", r["time"], r["price"],
                                 f"{r['left']}/{r['total']}", status(r))
                                for r in routes.values() if r["left"] or not self.only.get()])
        t = self.term.get().strip().lower()
        hits = [r for r in routes.values() if t in (r["id"].lower(), r["from"].lower(), r["to"].lower())] if t else []
        fill(self.search_tree, [(r["id"], f"{r['from']} -> {r['to']}", r["price"], r["left"]) for r in hits])
        self.search_note.config(text="" if hits or not t else f"No routes found for '{t}'.")
        self.route_box["values"] = [f"{r['id']}  {r['from']} -> {r['to']}  ({r['left']} free)" for r in routes.values()]
        fill(self.book_tree, [(b["id"], b["name"], b["route"], b["seats"], b["fare"], b["status"])
                              for b in bookings.values()])
        self.show_report()

    def book(self):
        name, age, seats = self.name.get().strip(), pos_int(self.age.get()), pos_int(self.seats.get())
        route = routes.get(self.route.get().split()[0]) if self.route.get() else None
        if not name:
            error = "Name cannot be empty."
        elif not age:
            error = "Age must be a positive whole number."
        elif not route:
            error = "Please choose a route."
        elif not seats:
            error = "Seats must be a positive whole number."
        elif seats > route["left"]:
            error = f"Only {route['left']} seat(s) available."
        else:
            error = None
        if error:
            return messagebox.showerror("Booking rejected", error)
        bid = f"B{next(booking_ids)}"
        fare = route["price"] * seats
        bookings[bid] = {"id": bid, "name": name, "age": age, "route": route["id"],
                         "seats": seats, "fare": fare, "status": "Confirmed"}
        route["left"] -= seats
        messagebox.showinfo("Booking confirmed", f"Booking ID: {bid}\nPassenger: {name}\n"
                            f"Route: {route['id']} ({route['from']} -> {route['to']})\nSeats: {seats}\n"
                            f"Fare per seat: Rs. {route['price']}\nTotal fare: Rs. {fare}")
        for var in (self.name, self.age, self.seats):
            var.set("")
        self.refresh()

    def cancel(self):
        picked = self.book_tree.selection()
        if not picked:
            return messagebox.showwarning("Cancel", "Select a booking first.")
        b = bookings[self.book_tree.item(picked[0])["values"][0]]
        if b["status"] != "Confirmed":
            return messagebox.showwarning("Cancel", f"Booking {b['id']} is already cancelled.")
        routes[b["route"]]["left"] += b["seats"]
        b["status"] = "Cancelled"
        messagebox.showinfo("Cancelled", f"Booking {b['id']} cancelled.\nSeats restored: {b['seats']}")
        self.refresh()

    def show_report(self):
        confirmed = 0
        seats, revenue = Counter(), Counter()
        for b in bookings.values():
            if b["status"] == "Confirmed":
                confirmed += 1
                seats[b["route"]] += b["seats"]
                revenue[b["route"]] += b["fare"]
        lines = ["BOOKING REPORT", f"Total bookings created: {len(bookings)}", f"Confirmed bookings: {confirmed}",
                 f"Cancelled bookings: {len(bookings) - confirmed}", f"Seats currently reserved: {seats.total()}",
                 f"Confirmed revenue: Rs. {revenue.total():,}",
                 f"Fully booked routes: {sum(not r['left'] for r in routes.values())}",
                 "", "ROUTE SCHEDULE BY DEPARTURE CITY"]
        for city in CITIES:
            lines.append(city)
            lines += [f"  {r['id']} -> {r['to']} | {r['time']}" for r in routes.values() if r["from"] == city] \
                or ["  No scheduled departures."]
        self.report_text.config(state="normal")
        self.report_text.delete("1.0", "end")
        self.report_text.insert("1.0", "\n".join(lines))
        self.report_text.config(state="disabled")


if __name__ == "__main__":
    App().mainloop()
