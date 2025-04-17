
from   _scripts.misc import read_json
from   datetime      import datetime
import threading  as thr
import socket     as soc
import threading  as thr
import subprocess as sub

class Receiver:
    defaults: dict = {
        "historypath": "/var/log/history.log", 
        "receiveport": 8000, 
        "connections": [
        ]
    }

    def __init__(self):
        self.rSocket: soc.socket
        self.rPort: int
        self.connections: int
        self.historyPath: str

    def loadConfig(self) -> None:
        try:
            data: dict = read_json("/etc/LanSend/config.json")
        except Exception as e:
            print(f"ERROR: Configs could not be loaded, trying defaults: {e} > /etc/LanSend/config.json")
            data: dict = Receiver.defaults
        self.rPort = data["receiveport"]
        self.connections = data["connections"]
        self.historyPath = data["historypath"]

    def loadSocket(self) -> None:
        self.rSocket = soc.socket(soc.AF_INET, soc.SOCK_STREAM)
        self.rSocket.bind(("0.0.0.0", self.rPort))

    def findHostByIP(self, ip) -> str:
        for machine in self.connections:
            if ip != machine["ip"]: 
                continue
            return machine["machinename"]

    def createWorker(self, conn, addr, machinename) -> None:
        thread: thr.Thread = thr.Thread(target=self.worker, args=(conn, addr, machinename,))
        thread.start()
        
    def worker(self, conn, addr, machinename) -> None:
        while True:
            packet: bytes = conn.recv(1024)
            if not packet:
                break
            msg: str = packet.decode("utf-8")

            self.sendNotification(machinename, msg)
            self.saveHistory(machinename, msg)
            
            

    def sendNotification(self, machinename, msg) -> None:
        print(machinename, ">", msg)
        sub.Popen(["notify-send", msg])

    def saveHistory(self, machinename, msg) -> None:
        try:
            with open(self.historyPath, mode="a") as f:
                time: str = datetime.now()
                f.write(
                    f"{time} {machinename}: {msg}\n"
                )
        except Exception as e:
            print("ERROR: Could not save history {e} > Try checking /var/log/LanSend/history.log")

    def run(self):
        self.loadConfig()
        self.loadSocket()

        print(f"Server listening @{self.rPort}")

        # Main-Loop for creating socket receiver workers
        self.rSocket.listen()
        while True:
            conn, addr = self.rSocket.accept()
            machinename = self.findHostByIP(addr[0])

            print(f"Connected to: ({addr}, {machinename})")
            
            self.createWorker(conn, addr, machinename)


if __name__ == "__main__":
    server: Receiver = Receiver()
    server.run()


            
