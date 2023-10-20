import random
import time
from typing import overload

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
    arrivalTime: int = -1
    serviceBegin: int = -1
    serviceTime: int = -1
    timeLeft: int = -1
    status: int = -1  # 1: dilayani 2:ngantre 3:selesai
    queueTime: int = 0
    name: str = "Unnamed Customer"

    def __init__(self,
                 name: str = "Unnamed Customer",
                 serviceBegin: int = -1,
                 arrivalTime: int = -1,
                 serviceTime: int = -1,
                 queued: bool = False
                 ) -> None:
        """
        Object Class untuk customer
        :param name: nama untuk customer
        :param serviceBegin: menit mulai service
        :param arrivalTime: menit kedatangan customer
        :param serviceTime: lama service time untuk melayani customer
        :param queued: True jika customer harus mengantri, False jika tidak
        """
        self.name = name
        self.serviceBegin = serviceBegin
        self.arrivalTime = arrivalTime
        self.serviceTime = serviceTime
        if queued:
            self.setQueueing()
        else:
            self.setServing()

    def setQueueing(self):
        self.status = 2

    def setServing(self):
        self.status = 1

    def setDone(self):
        self.status = 3
    @property
    def isDone(self) -> bool:
        return self.status == 3
    @property
    def isQueueing(self) -> bool:
        return self.status == 2
    @property
    def isServing(self) -> bool:
        return self.status == 1

    def __str__(self) -> str:
        return self.name

    def __repr__(self):
        return self.name
    @overload
    def __eq__(self, string:str)-> bool:...
    def __eq__(self, other):
        return self.name == other



class Server:
    currentCustomer: Customer = None
    status:int = 0 # 0 = idle , 1 = busy
    busyTime: int = 0
    idleTime: int = 0
    name: str = "unnamed server"
    queue: list = []
    serveredCustomer: list = []
    distribution: dict = {}
    @property
    def customer_count(self)->int:
        return len(self.serveredCustomer)
    @property
    def queue_count(self) -> int:
        return len(self.queue)
    @property
    def isBusy(self)->bool:
        return self.status == 1
    @property
    def isIdle(self)->bool:
        return self.status == 0
    @property
    def utility(self)->float:
        return self.busyTime / (self.busyTime + self.idleTime)

    def set_busy(self):
        self.status = 1

    def set_idle(self):
        self.status = 0

    def enqueue(self, customer):
        self.queue.append(customer)

    def dequeue(self):
        return self.queue.pop(0)

    def update(self, function):
        if self.isBusy:
            self.currentCustomer.timeLeft -= 1
            if self.currentCustomer.timeLeft <= 0:
                self.set_busy()
                doneCustomer = self.currentCustomer
                doneCustomer.setDone()
                self.currentCustomer = Customer('null')
                self.serveredCustomer.append(doneCustomer)
                function(f"DN!{doneCustomer} done | queue = {self.queue}")
            else:
                function(
                    f"IDL!current customer = {self.currentCustomer} | time left = {self.currentCustomer.timeLeft} | queue = {self.queue}")

        if self.queue:
            for customer in self.queue:
                customer.queuetime += 1

    def __init__(self,
                 serviceTimeDistribution: dict,
                 name: str = "unnamed server"
                 ) -> None:
        self.name = name
        self.distribution = serviceTimeDistribution
    def __str__(self) -> str:
        return self.name

    def __repr__(self):
        return self.name

class Simulation:
    # distribution: dict = {1: 0.1, 2: 0.2, 3: 0.3, 4: 0.25, 5: 0.1, 6: 0.05}
    distribution: dict = {7: 0.1, 3: 0.2, 9: 0.3, 8: 0.25, 6: 0.1, 2: 0.05}
    max_minute: int = 100
    function = lambda self, text: print(text.split("!")[-1]) if self.verbose else None
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
            if minute == next_arival:
                # while minute == (next_arival+interarivals.pop(0)):
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

    def __init__(self, verbose=True, **kwargs) -> None:
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
        self.verbose = verbose
        self.create_server()


if __name__ == '__main__':
    print(Customer("null") == Customer("nul"))
    pass
