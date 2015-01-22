import json
import re
from datetime import datetime, date, time, timedelta

class EventList:
    def __init__(self, data):
        self.data = data
        self.events = []
        self.events_shown_order = []
        for i in data['events']:
            self.make_event(i['title'], to_date(i['datetime']), i['UUID'])
        self.events.sort(key=lambda x: x.datetime)

    def id_collision(self, UUID):
        for i in self.events:
            if i.UUID == UUID:
                return True

    def make_event(self, title, datetime, UUID=0):
        self.events.append(Event(self, title, datetime, UUID))

    def user_add_event(self):
        try:
            print("\nNEW EVENT:")
            title = input("\nEnter a name:\n>>> ")
            new_datetime = user_input_datetime()
        except:
            input_err()
            return self.user_add_event()
        self.make_event(title, new_datetime)

    def select_event(self, num):
        for i in self.events:
            if i.UUID == self.events_shown_order[num - 1]:
                return i

    def delete_event(self, UUID):
        for i in self.events:
            if i.UUID == UUID:
                self.events.remove(i)

    def convert_dates_to_datetime(self):
        for i in self.events:
            i.datetime = to_date(i.datetime)

    def convert_dates_to_str(self):
        for i in self.events:
            i.datetime = to_str(i.datetime)

    def convert_events_to_dict(self):
        converted = []
        for i in self.events:
            converted.append({"title": i.title, "datetime": i.datetime,
                              "UUID": i.UUID})
        self.events = converted

    def print_events(self):
        print("\nLIST OF TRACKED EVENTS:")
        n = 1
        now = datetime.now()
        self.events_shown_order = []
        for i in self.events:
            self.events_shown_order.append(i.UUID)
            print("\n(" + str(n) + ") " + i.title)
            t = i.datetime
            print("WHEN: " + t.strftime('%a, %b %d, %Y'), end = "")
            if t.strftime('%H-%M') != "00-00":
                print(" at " + t.strftime('%I:%M %p'))
            else:
                print("")
            diff = t - now
            if now.year == t.year and now.month == t.month and \
               now.day == t.day:
                if t.hour == 0 and t.minute == 0:
                    print("TIME: Today!")
            elif diff > timedelta(minutes=0):
                print("TIME LEFT: " + natural_tdelta(diff))
            elif diff < timedelta(minutes=1) and diff > timedelta(minutes=-1):
                print("TIME: Right now!")
            elif diff < timedelta(minutes=0):
                print("TIME SINCE: " + natural_tdelta(-diff))
            n += 1

class Event:
    def __init__(self, parentList, title, datetime, UUID):
        self.parentList = parentList
        self.title = title
        self.datetime = datetime
        if UUID == 0:
            UUID += 1
            while self.parentList.id_collision(UUID):
                UUID += 1
        self.UUID = UUID

    def delete(self):
        self.parentList.delete_event(self.UUID)

def to_date(string):
    """Convert a string in the format YYYY-MM-DD-HH-MM to a datetime object."""
    return datetime.strptime(string, '%Y-%m-%d-%H-%M')

def to_str(date):
    """Convert a datetime object to a string in the format YYYY-MM-DD."""
    return date.strftime('%Y-%m-%d-%H-%M')

def input_err():
    """Display generic input error message to the user."""
    print("\nSorry, not a valid input. Please try again.\n")

def launch():
    """Launch the program and load user data from text file into memory."""
    def launch_msgs():
        print("\nWelcome to the countdown program. The day is " + \
              datetime.now().strftime('%a, %b %d, %Y') + ".")
        print("\nNote: Under the TIME SINCE/LEFT fields, a 'year' is exactly" +
              " 365 days, and a 'month' is exactly 30 days.")

    launch_msgs()
    eventList = EventList(json.load(open('data.txt')))
    main_screen(eventList)

def user_input_datetime():
    try:
        d = input("\nEnter a date in 'YYYY-MM-DD' format:\n>>> ").split("-")
        new_date = date(int(d[0]), int(d[1]), int(d[2]))
        t = input("\nEnter a time in 'HH-MM' format, or '00-00' for none:\n>>> ").split("-")
        new_time = time(int(t[0]), int(t[1]))
        return datetime.combine(new_date, new_time)
    except:
        input_err()
        return user_input_datetime()

def natural_tdelta(diff):
    def div_modder(dividend, divisors):
        if divisors == []:
            return [dividend]
        quotient, remainder = divmod(dividend, divisors[0])
        return [quotient] + div_modder(remainder, divisors[1:])

    def re_subber(str, subs):
        for s in subs:
            if type(s) != tuple:
                s = (s, "")
            str = re.sub(s[0], s[1], str)
        return str

    yrs, mos, wks, days = div_modder(diff.days, [365, 30, 7])
    hrs, mins, secs = div_modder(diff.seconds, [3600, 60])
    natural = str(yrs) + " years, " + str(mos) + " months, " + str(wks) + \
              " weeks, " + str(days) + " days, " + str(hrs) + " hours, " + \
              str(mins) + " minutes"
    subs = [('((^|\W)1 \w+)s', '\g<1>'), '(^|\W)0 \w+(,|$)', ',$', '^ ', 
            ('\d+ \w+$', 'and \g<0>'), '^and ', 
            ('(^\d+ \w+), and', '\g<1> and')]
    return re_subber(natural, subs)

def main_screen(eventList):
    def selected_event_menu(event):
        print("\nSELECTED EVENT: " + event.title)
        print("\nOPTIONS:")
        print("(1) Edit event title")
        print("(2) Edit event time and date")
        print("(3) Delete this event")
        
        try:
            choice = input("\n>>>")
            choice.strip().lower()
            if choice == '1':
                event.title = input("\nPlease enter a new title:\n>>> ")
            elif choice == '2':
                event.datetime = user_input_datetime()
            elif choice == '3':
                event.delete()
        except:
            input_err()
            selected_event_menu(event)

    eventList.print_events()

    try:
        print("\nOPTIONS:")
        print("(A) - Add an event to track.")
        print("(WQ) - Write the current data and quit the program.")
        print("(Q) - Quit the program without saving changes.")
        print("(#) - Enter the number of an event to select.")
        choice = input("\n>>> ")
        choice.strip().lower()
        if choice == 'a':
            eventList.user_add_event()
        elif choice == 'wq':
            write_quit(eventList)
            return
        elif choice == 'q':
            print("")
            return
        m = re.match(r'[0-9]+$', choice)
        if m:
            selected_event_menu(eventList.select_event(int(m.group())))
        else:
            input_err()
            main_screen(eventList)
            return
    except:
        input_err()
        main_screen(eventList)
        return

def write_quit(eventList):
    """Exports the user data to a text file in JSON and exits."""
    try:
        eventList.convert_dates_to_str()
        eventList.convert_events_to_dict()
        dict = {"events": eventList.events}
        with open('data.txt', 'w') as outfile:
            json.dump(dict, outfile, indent = 2, sort_keys = True)
        print("\nSuccessfully exported user data.")
    except:
        print("\nThere was a problem exporting the data.")
    print("")
    return

launch()