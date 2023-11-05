import random
import time
import numpy as np
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
    interarrival: int = -1
    arrivalTime: int = -1
    serviceBegin: int = -1
    serviceTime: int = -1
    timeLeft: int = -1
    status: int = -1  # 1: dilayani 2:ngantre 3:selesai
    queueTime: int = 0
    name: str = "Unnamed Customer"
    server = "not served"

    def __init__(self,
                 name: str = "Unnamed Customer",
                 interarrival: int = -1,
                 arrivalTime: int = -1,
                 ) -> None:
        """
        Object Class untuk customer
        :param name: nama untuk customer
        :param interarrival: jarak kedatangan dengan customer sebelumnya
        :param arrivalTime: menit kedatangan customer
        """
        self.name = name
        self.interarrival = interarrival
        self.arrivalTime = arrivalTime

    def serveBy(self, server, srvtime, srvbegin, queue=False):
        """
        method untuk serving customer
        :param server:
        :param srvtime:
        :param servbegin:
        :return:
        """
        self.server = server
        self.serviceTime = srvtime
        self.timeLeft = srvtime
        self.serviceBegin = srvbegin
        self.setServing() if not queue else self.setQueueing()

    def setQueueing(self):
        self.status = 2

    def setServing(self):
        self.status = 1

    def setDone(self):
        self.status = 3
        self.server.serveredCustomer.append(self)

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
    def __eq__(self, string: str) -> bool: ...

    def __eq__(self, other):
        return self.name == other


class Server:
    currentCustomer: Customer = Customer("null")
    status: int = 0  # 0 = idle , 1 = busy
    busyTime: int = 0
    idleTime: int = 0
    name: str = "unnamed server"
    queue: list = []
    serveredCustomer: list = []
    cumulativeDist: dict = {}

    @property
    def customer_count(self) -> int:
        return len(self.serveredCustomer)

    @property
    def queue_count(self) -> int:
        return len(self.queue)

    @property
    def isBusy(self) -> bool:
        return self.status == 1

    @property
    def isIdle(self) -> bool:
        return self.status == 0

    @property
    def utility(self) -> float:
        return self.busyTime / (self.busyTime + self.idleTime)

    @property
    def currentServiceTime(self):
        return self.currentCustomer.timeLeft

    @property
    def newCustomerWaitingTime(self):
        return self.currentServiceTime + sum([c.serviceTime for c in self.queue])

    @property
    def info(self)->str:
        return f"""
        server name    : {self.name}
        current status : {self.status} ({"busy" if self.isBusy else "idle"})
        utilization    : {self.utility * 100}% 
                         (idle time = {self.idleTime}, busy time = {self.busyTime})
        current customer: {self.currentCustomer} 
        current queue   : {len(self.queue)} customer(s)
                          {self.queue}
        customer served : {self.customer_count} customer(s)
                          {self.serveredCustomer}
        """


    def set_busy(self):
        self.status = 1

    def set_idle(self):
        self.status = 0

    def enqueue(self, customer):
        self.queue.append(customer)

    def dequeue(self) -> Customer:
        return self.queue.pop(0)

    def newServiceTime(self) -> float:
        randVal = random.random()
        return distribute_random(randVal, self.cumulativeDist)

    def update(self, function):

        if self.isIdle:
            function(f"SERVER INFO \t| {self} is idling...")
            self.idleTime += 1
        # function(f"\t== {self} updates ==")

        if self.isBusy:
            self.busyTime += 1
            self.currentCustomer.timeLeft -= 1
            if self.currentCustomer.timeLeft == 0:
                self.set_idle()
                doneCustomer = self.currentCustomer
                doneCustomer.setDone()
                self.currentCustomer = Customer('null')
                function(f"CUSTOMER INFO\t| {doneCustomer} is done ,nexts in {self}'s queue = {self.queue}")
            else:
                function(
                    f"SERVER INFO \t| {self}'s current customer = {self.currentCustomer} with service time left = {self.currentCustomer.timeLeft}")

        if self.queue:
            if self.isIdle:
                nextInQueue = self.dequeue()
                self.currentCustomer = nextInQueue
                self.set_busy()
                function(f"SERVER INFO \t| {self} dequeued {nextInQueue} from queue, next in queue : {self.queue}")

            for customer in self.queue:
                customer.queueTime += 1


    def reset(self):
        """
        method untuk mereset server
        :return:
        """
        self.currentCustomer = Customer("null")
        self.status = 0
        self.busyTime = 0
        self.idleTime = 0
        self.queue = []
        self.serveredCustomer = []

    def __init__(self,
                 srvtDist,
                 name: str = "unnamed server"
                 ) -> None:
        """
        object class untuk server
        :param srvtDist: distribusi service time untuk server yang akan dibuat
        :param name: nama dari server
        """
        self.name = name
        self.cumulativeDist = count_cumulative(srvtDist)

    def __str__(self) -> str:
        return self.name

    def __repr__(self):
        return self.name



class SimulationModel:
    max_minute: int = -1
    default_maxmins: int = -1
    current_minute: int = 1
    cNumber: int = 1
    delay: float = 0.0
    servers: list = []
    cumulativeDist: dict = {}
    interarival: int = -1

    @property
    def server_count(self):
        return len(self.servers)

    def __init__(self,
                 servers,
                 intrArrivalDist,
                 max_minute=10,
                 delay=0.0,
                 ) -> None:
        """
        object class untuk model simulasi
        :param servers: list server server pada simulasi
        :param intrArrivalDist: distribusi interarival dari customer
        :param max_minute: menit maksimal simulasi berjalan
        :param delay: delay dari setiap iterasi simulasi
        """
        self.servers = servers
        self.max_minute = max_minute
        self.default_maxmins = max_minute
        self.delay = delay
        self.cumulativeDist = count_cumulative(intrArrivalDist)

    def newInterArrival(self):
        randVal = random.random()
        self.interarival = distribute_random(randVal, self.cumulativeDist)

    def servers_update(self, f):
        for server in self.servers:
            server.update(f)

    def run(self, ofunc=print, verbose=True, reset=True, add_minutes=0):
        """
        method untuk menjalankan simulasi
        :param ofunc: fungsi output yang akan digunakan untuk menampilkan hasil simulasi berkala
        :param verbose: jika True maka akan menjalankan fungsi yang diberikan pada 'ofunc'
        :param reset: jika True maka akan mengulang kondisi simulasi dan server ke kondisi awal
        :param add_minutes: menambah waktu (menit) untuk menjalankan simulasi
        :return:
        """
        self.max_minute += add_minutes
        func = ofunc if verbose else lambda x: None
        self.reset() if reset else None
        assert self.current_minute <= self.max_minute, \
            f"current minute {self.current_minute} >= max minute {self.max_minute}, stopping simulation"
        func("========== SIMULATION STARTS ==========")
        self.newInterArrival()
        func(f"SIMULATION INFO\t| next customer interarrival = {self.interarival}")
        nextArrival = self.current_minute + self.interarival
        while self.current_minute <= self.max_minute:
            func(f"========== minute {self.current_minute} start ==========")
            # func("\t== simulation updates ==")
            while self.current_minute == nextArrival:
                cArrive = Customer(name=f"Customer {self.cNumber}",
                                   interarrival=self.interarival, 
                                   arrivalTime=self.current_minute)
                func(f"CUSTOMER INFO\t| {cArrive} has arrived")
                serverBusy, server = self.choseServer()
                func(
                    f"SERVER INFO \t| {server} has choosen for {cArrive} with current status : {'busy' if serverBusy else 'idle'}")
                if serverBusy:
                    server.enqueue(cArrive)
                    serviceTime = server.newServiceTime()
                    serviceBegin = server.currentServiceTime + self.current_minute
                    cArrive.serveBy(server=server, srvtime=serviceTime, srvbegin=serviceBegin, queue=True)
                    func(f"CUSTOMER INFO\t| {cArrive} enqueued to {server}'s queue : {server.queue}")
                else:
                    serviceTime = server.newServiceTime()
                    cArrive.serveBy(server=server, srvtime=serviceTime, srvbegin=self.current_minute)
                    server.currentCustomer = cArrive
                    server.set_busy()
                    func(f"SERVER INFO \t| {server} serving new customer : {cArrive}, with service time : {serviceTime}")

                self.newInterArrival()
                func(f"SIMULATION INFO\t| next customer interarrival = {self.interarival}")
                nextArrival = self.current_minute + self.interarival
                self.cNumber += 1

            self.servers_update(func)
            func(f'========== minute {self.current_minute} end ==========\n')
            self.current_minute += 1
            time.sleep(self.delay)
        func("========== SIMULATION ENDS ==========")

    def choseServer(self):
        """
        method untuk memilih server mana yang akan melayani customer
        :return: tuple(isBusy:bool, server:Server)
        """
        Statuses = [s.status for s in self.servers]
        if sum(Statuses) == 0:  # jika semua server idle
            sSelected = self.servers[0]  # server pertama yang dipilih
            return sSelected.isBusy, sSelected

        if 0 < sum(Statuses) < self.server_count:  # jika beberapa server busy dan beberapa tidak
            selectedIdx = np.argmin(Statuses)  # server pertama dengan status idle
            sSelected = self.servers[selectedIdx]  # yang akan dipilih
            return sSelected.isBusy, sSelected

        if sum(Statuses) == self.server_count:  # jika semua server busy
            waitTimes = [s.newCustomerWaitingTime
                             for s in self.servers]
            selectedIdx = np.argmin(waitTimes)  # server pertama dengan waktu tunggu terendah
            sSelected = self.servers[selectedIdx]  # yang akan dipilih
            return sSelected.isBusy, sSelected


    def reset(self):
        self.current_minute = 1
        self.max_minute = self.default_maxmins
        self.cNumber = 1
        for server in self.servers:
            server.reset()


if __name__ == '__main__':
    distribution1 = {1: 0.1, 2: 0.2, 3: 0.3, 4: 0.25, 5: 0.1, 6: 0.05}
    distribution2 = {7: 0.1, 3: 0.2, 9: 0.3, 8: 0.25, 6: 0.1, 2: 0.05}
    distribution3 = {3: 0.2, 2: 0.2, 1: 0.05, 0: 0.55}

    simulator = SimulationModel([
        Server(distribution1, name="Server1"),
        Server(distribution1, name="server2"),
        Server(distribution1, name="server3"),
        Server(distribution1, name="server4"),
    ],
        intrArrivalDist=distribution3,
        max_minute=1000,
        delay=0
                )
    simulator.run(verbose=False)
    # simulator.resetSimulation()
    simulator.continueRun(add_minute=5, verbose=True)
