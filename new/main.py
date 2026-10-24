"""Smart Bus Ticket Booking System - in-memory only (data is lost on exit)."""
from collections import Counter, defaultdict
from itertools import count

CITIES = ("Karachi", "Hyderabad", "Sukkur", "Mirpur Khas", "Lahore")
KEYS = ("route_id", "departure_city", "destination_city", "departure_time", "ticket_price", "total_seats")
ROUTES = (("R101", "Karachi", "Hyderabad", "08:00 AM", 1200, 40),
          ("R102", "Karachi", "Sukkur", "09:30 AM", 2000, 36),
          ("R103", "Hyderabad", "Mirpur Khas", "11:00 AM", 800, 32),
          ("R104", "Karachi", "Lahore", "07:00 PM", 5000, 45),
          ("R105", "Sukkur", "Hyderabad", "02:00 PM", 1500, 30))

routes = {r[0]: dict(zip(KEYS, r), available_seats=r[5]) for r in ROUTES}  # id -> route, in order
bookings: dict[str, dict] = {}   # id -> booking; insertion order = history, keys = issued IDs
booking_ids = count(1001)


def num(prompt):
    """Positive whole number, else None."""
    s = input(prompt).strip()
    return int(s) if s.isdecimal() and int(s) > 0 else None


def journey(r):
    return f"{r['departure_city']} -> {r['destination_city']}"


def route_line(r):
    return f"{r['route_id']} | {journey(r)} | Rs. {r['ticket_price']} | {r['available_seats']} seats available"


def schedule():
    by_city = defaultdict(list)
    for r in routes.values():
        by_city[r["departure_city"]].append(f"  {r['route_id']} -> {r['destination_city']} | {r['departure_time']}")
    print("\n".join(["\nROUTE SCHEDULE BY DEPARTURE CITY",
                     *(line for c in CITIES for line in (c, *(by_city[c] or ["  No scheduled departures."])))]))


def list_routes():
    mode = input("\n1) All routes  2) Only with seats  3) Schedule by city (default 1): ").strip()
    if mode == "3":
        return schedule()
    rows = [f"{n:<4}{r['route_id']:<7}{journey(r):<28}{r['departure_time']:<10}{'Rs.' + str(r['ticket_price']):<10}"
            + (f"{r['available_seats']}/{r['total_seats']}" if r["available_seats"] else "Fully Booked")
            for n, r in enumerate(routes.values(), 1) if mode != "2" or r["available_seats"]]
    print("\n".join(["\nAVAILABLE BUS ROUTES", f"{'No.':<4}{'Route':<7}{'Journey':<28}{'Depart':<10}{'Fare':<10}Seats", *rows]))


def search():
    if not (t := input("Search by route ID or city: ").strip()):
        return print("Please enter a route ID or city name.")
    hits = [hit] if (hit := routes.get(t.upper())) else [
        r for r in routes.values() if t.lower() in (r["departure_city"].lower(), r["destination_city"].lower())]
    print("\n".join(map(route_line, hits)) or f"No routes found for '{t.lower()}'.")


def book():
    if not (name := input("Passenger name: ").strip()):
        return print("Rejected: name cannot be empty.")
    if not (age := num("Passenger age: ")):
        return print("Rejected: age must be a positive whole number.")
    if not (route := routes.get(input("Route ID: ").strip().upper())):
        return print("Rejected: route not found.")
    if not (seats := num("Number of seats: ")):
        return print("Rejected: seats must be a positive whole number.")
    if seats > route["available_seats"]:
        return print(f"Rejected: only {route['available_seats']} seat(s) available.")

    bid = f"B{next(booking_ids)}"    # counter never repeats, so IDs are unique
    fare = route["ticket_price"] * seats
    bookings[bid] = {"booking_id": bid, "passenger_name": name, "passenger_age": age,
                     "route_id": route["route_id"], "seats": seats, "total_fare": fare, "status": "Confirmed"}
    route["available_seats"] -= seats
    print(f"\nBooking confirmed!\nBooking ID: {bid}\nPassenger: {name}\n"
          f"Route: {route['route_id']} ({journey(route)})\nSeats booked: {seats}\n"
          f"Fare per seat: Rs. {route['ticket_price']}\nTotal fare: Rs. {fare}\nStatus: Confirmed")


def my_bookings():
    print("\n".join(["\nMY BOOKINGS", *(
        f"{n}. {b['booking_id']} | {b['passenger_name']} | {b['route_id']} | {b['seats']} seat(s) | "
        f"Rs. {b['total_fare']} | {b['status']}" for n, b in enumerate(bookings.values(), 1))])
          if bookings else "No bookings found.")


def cancel():
    bid = input("Enter booking ID to cancel: ").strip().upper()
    if not (b := bookings.get(bid)):
        return print(f"Booking ID '{bid}' not found.")
    if b["status"] != "Confirmed":
        return print(f"Booking {bid} is already cancelled. No seats restored.")
    r = routes[b["route_id"]]
    r["available_seats"] += b["seats"]
    b["status"] = "Cancelled"
    print(f"Booking {bid} has been cancelled.\nSeats restored: {b['seats']}\n"
          f"Route {r['route_id']} available seats: {r['available_seats']}")


def availability():
    only = input("Show only routes with seats? (y/n): ").strip().lower() == "y"
    rows = [f"{r['route_id']} | {journey(r)} | {r['available_seats']}/{r['total_seats']} | "
            + ("Fully Booked" if not r["available_seats"] else
               "Available" if r["available_seats"] == r["total_seats"] else "Partially Booked")
            for r in routes.values() if r["available_seats"] or not only]
    print("\n".join(["\nSEAT AVAILABILITY", *rows]) if rows else "No routes have seats available.")


def report():
    confirmed = 0
    seats, revenue = Counter(), Counter()            # per route ID
    for b in bookings.values():                      # single pass
        if b["status"] == "Confirmed":
            confirmed += 1
            seats[b["route_id"]] += b["seats"]
            revenue[b["route_id"]] += b["total_fare"]
    rows = [f"  {rid}: {s} seat(s), Rs. {revenue[rid]:,}" for rid, s in seats.items()] or ["  None."]
    print("\n".join(["\nBOOKING REPORT", f"Total bookings created: {len(bookings)}",
                     f"Confirmed bookings: {confirmed}", f"Cancelled bookings: {len(bookings) - confirmed}",
                     f"Seats currently reserved: {seats.total()}", f"Confirmed revenue: Rs. {revenue.total():,}",
                     f"Fully booked routes: {sum(not r['available_seats'] for r in routes.values())}",
                     "\nConfirmed bookings by route:", *rows]))


ITEMS = ("View Available Routes", "Search for a Route", "Book a Ticket", "View My Bookings",
         "Cancel a Booking", "View Seat Availability", "Generate Booking Report", "Exit")
MENU = "\nSMART BUS RESERVATION SYSTEM\n" + "=" * 32 + "\n" + \
       "\n".join(f"{i}. {t}" for i, t in enumerate(ITEMS, 1)) + "\n" + "=" * 32
ACTIONS = dict(zip("1234567", (list_routes, search, book, my_bookings, cancel, availability, report)))


def main():
    while (choice := input(MENU + "\nEnter your choice: ").strip()) != "8":
        ACTIONS.get(choice, lambda: print("Invalid choice. Please enter a number from 1 to 8."))()
    print("Thank you for using Smart Bus. Goodbye!")


if __name__ == "__main__":
    main()
