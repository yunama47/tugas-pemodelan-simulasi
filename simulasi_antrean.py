import builtins
import random


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


class Server:
    def __init__(self) -> None:
        self.busy = False
        self.queue = []
        self.current_customer = None
        self.servered_customers = []

    def set_busy(self, b):
        self.busy = b

    def enqueue(self, customer):
        self.queue.append(customer)

    def dequeue(self):
        return self.queue.pop(0)

    def update(self):
        if self.busy:
            self.curent_customer.servicetime -= 1
            if self.curent_customer.servicetime == 0:
                self.set_busy(False)
                self.servered_customers.append(self.curent_customer)
                self.curent_customer = None

        if self.queue:
            for customer in self.queue:
                customer.queuetime += 1


class Customer:
    def __init__(self, no_customer, srtime) -> None:
        self.servicetime = srtime
        self.queuetime = 0
        self.name = f"customer {no_customer}"

    def __str__(self) -> str:
        return self.name


class Simulation:
    distribution: dict = {1: 0.1, 2: 0.2, 3: 0.3, 4: 0.25, 5: 0.1, 6: 0.05}
    max_minute: int = 100
    function = print
    server: Server = Server()

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
            function(f"=== minute {minute} ===")
            if minute == next_arival:
                if not server.busy and not server.queue:
                    service_time = distribute_random(random.random(), cumulative)
                    service_done = minute + service_time
                    server.curent_customer = Customer(no_customer, service_time)
                    server.set_busy(True)
                    function(
                        f"{server.curent_customer} arrive | service time = {service_time} | done at minute {service_done}")

                elif server.busy:
                    service_time = distribute_random(random.random(), cumulative)
                    new_customer = Customer(no_customer, service_time)
                    server.enqueue(new_customer)
                    function(f"{new_customer} arrive | service time = {service_time} | enqueued")

                next_arival += interarivals.pop(0)
                no_customer += 1

            elif not server.busy and server.queue:
                next_customer = server.dequeue()
                server.curent_customer = next_customer
                server.set_busy(True)
                function(f"{next_customer} dequeued")

            if server.busy:
                function(
                    f"current customer = {server.curent_customer} | time left = {server.curent_customer.servicetime} | length queue = {len(server.queue)}")
            else:
                function(f"server idle... next arrival in minute {next_arival}")

            server.update()
            function("\n")

    def __init__(self, **kwargs) -> None:
        """
        parameter =
        distribution : distribusi service time
        max_minute : menit maksimal system berjalan
        function : fungsi yang akan digunakan untuk menampilkan progress
        """
        if kwargs.get("distribusi"):
            self.distribution = kwargs["distribusi"]
        if kwargs.get("max_minute"):
            self.max_minute = kwargs["max_minute"]
        if kwargs.get("function"):
            self.function = kwargs["function"]


if __name__ == "__main__":
    a = {3: 0.19, 5: 0.2, 6: 0.3, 7: 0.3, 10: 0.01}
    print(count_cumulative(a))
    # print(count_cumulative(a))
