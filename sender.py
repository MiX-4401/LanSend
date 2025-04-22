
from typing        import Union, NewType
from _scripts.misc import read_json
import subprocess as sub
import socket     as soc

IP = NewType("IP", str)
HOSTNAME = NewType("HOSTNAME", str)

class Sender:
    defaults: dict = {
        "historypath": "/var/log/history.log", 
        "receiveport": 8000, 
        "connections": [

        ],
        "blacklist": [
            
        ]
    }

    def __init__(self):
        self.sSocket: soc.socket
        self.rPort: int

        self.loadConfig()
        self.loadSocket()

    def loadConfig(self) -> None:
        try:
            data: dict = read_json("/etc/LanSend/config.json")
        except Exception as e:
            print(f"ERROR: Configs could not be loaded, trying defaults: {e} > /etc/LanSend/config.json")
            data: dict = Sender.defaults
        self.rPort = data["receiveport"]
        self.connections = data["connections"]
    
    def loadSocket(self) -> None:
        self.sSocket = soc.socket(soc.AF_INET, soc.SOCK_STREAM)

    def findIpByName(self, hostname) -> str:
        for machine in self.connections:
            if hostname != machine["machinename"]: 
                continue
            return machine["ip"]
        return "Unkown"
        
    def findNameByIP(self, ip:str) -> str:
        for machine in self.connections:
            if ip != machine["ip"]: 
                continue
            return machine["machinename"]
        return "Unkown"

    def establishConnection(self, ip:str, silent:bool=False) -> None:
        try:
            self.sSocket.connect((ip, self.rPort))
            return True
        except Exception as e:
            if not silent: print(f"Could not connect to {ip}: {e}")
            return False
        
    # def checkOnline(self, ip:str) -> None:
    #     result = sub.run(["ping", ip], capture_output=True)
    #     return result

    def broadcast(self, msg:str):
        for machine in self.connections:
            ip = machine["ip"]
            machinename = machine["machinename"]
            result = self.establishConnection(ip)
            if not result: continue 
            self.sSocket.sendall(msg.encode("utf-8"))
            print(f"Broadcasted to ({ip}, {machinename})")
        self.sSocket.close()

    def send(self, msg:str, host:Union[IP,HOSTNAME]):
        if not "." in host: ip: str = self.findHostByName(host)
        else: ip = host
        result = self.establishConnection(ip)
        if not result: return
        self.sSocket.sendall(msg.encode("utf-8"))
        self.sSocket.close()
    
    def pingAll(self):
        for machine in self.connections:
            ip = machine["ip"]
            machinename = machine["machinename"]
            result = self.establishConnection(ip, silent=True)
            if result: print(f"({ip}, {machinename}): LanSend.service is online")
            else: print(f"({ip}, {machinename}): LanSend service is offline")
        self.sSocket.close()

    def ping(self, host:Union[IP,HOSTNAME]):
        if not "." in host: 
            machinename = host
            ip: str = self.findIpByName(machinename)
        else: 
            ip = host
            machinename = self.findNameByIP(ip)
        result = self.establishConnection(ip, silent=True)
        if result: print(f"({ip}, {machinename}): LanSend.service is online")
        else: print(f"({ip}, {machinename}): LanSend service is offline")
        self.sSocket.close()




