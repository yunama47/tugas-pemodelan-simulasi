import random
import time


def avg_distribution(distribution: dict):
    a = 0
    for key, val in distribution.items():
        a += key * val
    return a


def count_cumulative(distribution: dict):
    cumulative = {}
    keys = list(distribution.keys())
    vals = list(distribution.values())

    for i in range(len(distribution)):
        if i == 0:
            key, val = keys[i], vals[i]
            cumulative[key] = val
            continue
        key, prev, val = keys[i], keys[i - 1], vals[i]
        cumulative[key] = round(cumulative[prev] + val, 3)
    return cumulative


def distribute_random(ran: float, cumulative: dict):
    for key, val in cumulative.items():
        if ran <= val:
            return key
    raise ValueError("nilai random melebihi 1!")


class Customer:
    servicebegin = None
    arrivaltime: int = -1
    status: int = -1 #1: dilayani 2:ngantre 3:selesai
    def __init__(self, name, srtime) -> None:
        self.servicetime = srtime
        self.timeleft = srtime
        self.queuetime = 0
        self.name = name

    def __str__(self) -> str:
        return self.name

    def __repr__(self):
        return self.name


class Server:
    current_customer: Customer = None
    busytime: int = 0
    idletime: int = 0
    customercount: int = 0
    utility: float = 0.0
    name: str = ""
    def __init__(self) -> None:
        self.busy = False
        self.queue = []
        self.servered_customers = []

    def set_busy(self, b):
        self.busy = b

    def enqueue(self, customer):
        self.queue.append(customer)

    def dequeue(self):
        nextCustomer: Customer = self.queue.pop(0)
        return nextCustomer

    def update(self, function):
        if self.busy:
            self.current_customer.timeleft -= 1
            if self.current_customer.timeleft == 0:
                self.set_busy(False)
                doneCustomer = self.current_customer
                self.current_customer = None
                self.servered_customers.append(doneCustomer)
                function(f"DN!{doneCustomer} done | queue = {self.queue}")
            else:
                function(
                    f"IDL!current customer = {self.current_customer} | time left = {self.current_customer.timeleft} | queue = {self.queue}")

        if self.queue:
            for customer in self.queue:
                customer.queuetime += 1
        # function(
        #     f"=================================\ncurrent = {self.current_customer}, busy = {self.busy}, queue = {self.queue}\n== debug [end] ==")


class Simulation:
    # distribution: dict = {1: 0.1, 2: 0.2, 3: 0.3, 4: 0.25, 5: 0.1, 6: 0.05}
    distribution: dict = {7: 0.1, 3: 0.2, 9: 0.3, 8: 0.25, 6: 0.1, 2: 0.05}
    max_minute: int = 100
    function = lambda self, text: print(text.split("!")[-1])
    delay: float = 0.0
    server: Server = None
    idle_time: int = 0
    def create_server(self):
        self.server = Server()

    def single_server_simulation(self):
        service_time_dist = self.distribution
        max_minute = self.max_minute
        function = self.function
        server = self.server

        next_arival = 0
        interarivals = [random.randrange(1, 8) for i in range(int(max_minute / 2))]
        cumulative = count_cumulative(service_time_dist)
        no_customer = 1

        for minute in range(max_minute):
            function(f"IDL!=== minute {minute} ===")
            # function(
            #     f"== debug [start] ==\ncurrent = {server.current_customer}, busy = {server.busy}, queue = {server.queue}\n=================================")
            if minute == next_arival:
            #while minute == (next_arival+interarivals.pop(0)):
                if not server.busy and not server.queue:
                    service_time = distribute_random(random.random(), cumulative)
                    service_done = minute + service_time - 1
                    server.current_customer = Customer(f"Customer {no_customer}", service_time)
                    server.set_busy(True)
                    function(
                        f"CRI!{server.current_customer} arrive | service time = {service_time} | done at minute {service_done}")

                elif server.busy:
                    service_time = distribute_random(random.random(), cumulative)
                    new_customer = Customer(f"Customer {no_customer}", service_time)
                    server.enqueue(new_customer)
                    function(f"CRQ!{new_customer} arrive | service time = {service_time} | enqueued")

                next_arival += interarivals.pop(0)
                no_customer += 1

            if not server.busy and server.queue:
                next_customer = server.dequeue()
                server.current_customer = next_customer
                server.set_busy(True)
                function(f"DEQ!{next_customer} dequeued")

            elif not server.busy and not server.queue:
                function(f"IDL!server idle... next arrival in minute {next_arival}")
                self.idle_time += 1

            server.update(function)
            function("IDL!\n")
            time.sleep(self.delay)

    def __init__(self, **kwargs) -> None:
        """
        class untuk simulasi
        :param distribution: distribusi service time
        :param max_minute: menit maksimal system berjalan
        :param function: fungsi yang akan digunakan untuk menampilkan progress
        """
        if kwargs.get("distribusi"):
            self.distribution = kwargs["distribusi"]
        if kwargs.get("max_minute"):
            self.max_minute = kwargs["max_minute"]
        if kwargs.get("function"):
            self.function = kwargs["function"]
        if kwargs.get("delay"):
            self.delay = kwargs["delay"]

        self.create_server()
