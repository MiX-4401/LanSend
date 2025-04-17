from typing        import Union, NewType
from json          import dump
from _scripts.misc import read_json
from sender        import Sender
import subprocess as sub
import click      as cli


IP = NewType("IP", str)
HOSTNAME = NewType("HOSTNAME", str)


@cli.group()
@cli.pass_context
def myCli(ctx):
    """LanSend for sending messages via local-area-networks"""
    
    defaults: dict = {
        "historypath": "/var/log/history.log", 
        "receiveport": 8000, 
        "connections": [
        ]
    }

    ctx.ensure_object(dict)
    try: 
        ctx.obj["config"] = read_json("/etc/LanSend/config.json")
    except FileNotFoundError as e:
        ctx.obj["config"] = defaults
    ctx.obj["sender"] = Sender()
    

@myCli.command("send")
@cli.argument("host")
@cli.argument("msg")
@cli.pass_context
def CLISend(ctx, host:Union[IP,HOSTNAME], msg:str) -> None:
    """Send to specific machine"""

    ctx.obj["sender"].send(host=host, msg=msg)

@myCli.command("broadcast")
@cli.argument("msg")
@cli.pass_context
def CLIBroadcast(ctx, msg:str) -> None:
    """Send to ALL machines"""
    
    ctx.obj["sender"].broadcast(msg=msg)

@myCli.command("history")
@cli.option("-a", "--all",     default=False, is_flag=True, type=bool, help="number of messages")
@cli.option("-c", "--count",   default=1,    type=int, help="number of messages")
@cli.pass_context
def CLIHistory(ctx, all:bool, count:int) -> None:
    """Get received message history"""
    
    with open(ctx.obj["config"]["historypath"], "r") as f:
        data:     list = f.readlines()
        maxLines: int = len(data)

        if all:
            cli.echo("run")
            for x in range(1,maxLines):
                cli.echo(data[x] + "\n")
        elif count:
            if count > maxLines:
                count = maxLines 

            for x in range(1, 1 + count):
                cli.echo(data[-x] + "\n")


@myCli.command("config")
@cli.option("-a", "--add-machine",    nargs=2, metavar="IP, NAME")
@cli.option("-r", "--remove-machine", nargs=1, metavar="NAME")
@cli.option("-s", "--show-machines",  is_flag=True)
@cli.option("-p", "--default-port",   nargs=1, metavar="PORT")
@cli.pass_context
def CLIConfig(ctx, add_machine, remove_machine, show_machines, default_port) -> None:
    """Modify the LanSend configs"""

    if add_machine:
        ip, machinename = add_machine
        ctx.obj["config"]["connections"].append({"machinename": machinename, "ip": ip})
    elif remove_machine:
        machinename = remove_machine
        for i,x in enumerate(ctx.obj["config"]["connections"]):
            if x["machinename"] != machinename: continue
            ctx.obj["config"]["connections"].pop(i)
    elif show_machines:
        for x in ctx.obj["config"]["connections"]:
            ip:          str = x["ip"]
            machinename: str = x["machinename"]
            
            cli.echo(f"IP: {ip}")
            cli.echo(f"MACHINENAME: {machinename}")
    elif default_port:
        ctx.obj["config"]["receiveport"] = default_port
        
    with open("/etc/LanSend/config.json", "w") as f:
        dump(ctx.obj["config"], f)


@myCli.command("start-service")
def CLIStartService() -> None:
    """SystemD - Start the lansend.service daemon"""
    try:
        sub.run(["systemctl", "--user", "start", "lansend"])
        cli.echo("lansend.service has started")
    except:
        print("ERROR: There was an unexpected error when attempting to start this service")

@myCli.command("stop-service")
def CLIStopService() -> None:
    """SystemD - Stop the landsend.service daemon"""
    try:
        sub.run(["systemctl", "--user", "stop", "lansend"])
        cli.echo("lansend.service has stopped")
    except:
        print("ERROR: There was an unexpected error when attempting to stop this service")

    
myCli()
