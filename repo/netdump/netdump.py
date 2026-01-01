import ipaddress
import logging
import os
import socket
import sys
import threading
import time
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from logging.handlers import RotatingFileHandler

workth = True

if sys.argv[-1].startswith("-"):
    external_ip = sys.argv[-1][1:]

else:
    external_ip = urllib.request.urlopen("https://ipinfo.io/ip").read().decode("utf-8")

try:
    import psutil
    from getmac import get_mac_address
except ImportError:
    print("Installing missing packages...")
    os.system("python -m pip install psutil getmac")
    time.sleep(1)
    os.system(" ".join(sys.argv))
    time.sleep(1)
    exit()

dumpdir = f"network_dump_{external_ip}"
portsdir = os.path.join(dumpdir, "OPEN_PORTS")

loaded_ips = 0
scanned_ips = 0

socket.setdefaulttimeout(3)

_cpu_count = os.cpu_count()
globalthreads = min(_cpu_count * 64, 1024)  # type: ignore
localthreads = min(_cpu_count * 2, 32)  # type: ignore
lock = threading.Lock()
flock = threading.Lock()
start_time = time.time()
log_file = os.path.join(dumpdir, "log.txt")
timeouts = []
mac_addresses = {}
dumped_dns = {}
devices = []

istermux = False
if "/data/data/com.termux/files/home" in os.path.expanduser("~"):
    istermux = True

_DEVICE = {
    "windows": [137, 138, 139, 5985, 5986, 3389, 135, 50550, 445],
    "ios": [49152, 62078],
    "linux?": [22, 6000, 21],
}

_PORTS = {
    "veyon": [11100, 11200, 11300],
    "ssh": [22],
    "telnet": [23],
    "anydesk": [7070],
    "msrpc": [135],
    "rpc": [111],
    "smb": [445],
    "netbios": [137, 138, 139],
    "rdp": [3389],
    "winrm": [5985, 5986],
    "iphone": [49152, 62078],
    "ftp": [21],
    "vnc": [5800, 5900],
    "http": [80],
    "https": [443],
    "upnp": [1900, 5000, 2869],
    "heyec": [50550],
    "termux-backdoor": [48573],
    "x11": [6000],
    "radmin": [4899],
}

vulnerabilities_ports = [11100, 11200, 11300, 48573, 50550]

ports = {port: service for service, _ports in _PORTS.items() for port in _ports}
dev_ports = {port: service for service, _ports in _DEVICE.items() for port in _ports}


class Network:
    @staticmethod
    def getranges():
        networks = []
        for _, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    ip = addr.address
                    try:
                        if (
                            not ip.startswith("127.")
                            and not ip.startswith("169.254.")
                            and not ip.startswith("172.21.")
                        ):
                            network = ipaddress.IPv4Network(
                                f"{ip}/{addr.netmask}", strict=False
                            )
                            if not network.is_loopback and not network.is_link_local:
                                nrange = (
                                    str(network.network_address)
                                    + "/"
                                    + str(network.prefixlen)
                                )
                                if istermux:
                                    if nrange.endswith("/8"):
                                        continue

                                if nrange != "172.24.16.0/20":
                                    networks.append(nrange)
                                    logging.info(f"found ip range {nrange}")

                    except ValueError:
                        pass

        return networks

    @staticmethod
    def scanport(host: str, port: int) -> bool:
        global timeouts
        try:
            _start_time = time.time()
            with socket.socket() as s:
                result = s.connect_ex((host, port))
            opened = result == 0

            if opened:
                timeout = time.time() - _start_time
                if timeout != 0.0000:
                    with lock:
                        timeouts.append(timeout)
                else:
                    logging.info(f"{host}:{port} timeout very small")

            return opened

        except:
            return False

    @staticmethod
    def getservice(port: int) -> str:
        try:
            portname = socket.getservbyport(port, "tcp")
        except:
            portname = "unknown"
        return ports.get(port, portname)


def progress():
    global loaded_ips, scanned_ips, workth
    while workth:
        print(
            f"time: {time.time() - start_time:.2f}, loaded ips: {loaded_ips}, scanned ips: {scanned_ips} [{loaded_ips}/{scanned_ips}]"
        )
        time.sleep(3)


def localscanner(ip: str):
    global scanned_ips, mac_addresses, dumped_dns, devices
    try:
        open_ports = []
        hostname = None
        mac_address = get_mac_address(ip=ip)

        if mac_address:
            with lock:
                mac_addresses[ip] = mac_address

        with ThreadPoolExecutor(
            localthreads, thread_name_prefix="local_scan"
        ) as local_executor:
            raw_ports = local_executor.map(
                Network.scanport, [ip] * len(ports.keys()), ports.keys()
            )

        for c_port, c_status in zip(ports.keys(), raw_ports):
            if c_status:
                open_ports.append(c_port)

        try:
            hostname = socket.gethostbyaddr(ip)[0]
            with lock:
                dumped_dns[ip] = hostname
        except:
            pass

        if open_ports != []:
            dir_path = os.path.join(dumpdir, ip)
            os.makedirs(dir_path, exist_ok=True)
            local_dev = []
            with open(os.path.join(dir_path, "ports.txt"), "w", encoding="utf-8") as f:
                temp = ""
                for port in open_ports:
                    port_file = os.path.join(portsdir, f"{port}.txt")
                    service = Network.getservice(port)
                    temp += f"{port}: {service}\n"

                    if os.path.exists(port_file):
                        open_mode = "a"
                    else:
                        open_mode = "w"

                    with flock:
                        with open(port_file, mode=open_mode, encoding="utf-8") as portf:
                            portf.write(f"{ip}\n")

                    if port in vulnerabilities_ports:
                        vulnerabilities_file = os.path.join(
                            dumpdir, f"vulnerable_ips.txt"
                        )
                        logging.info(f"found vulnerable port on {ip} - {port}")

                        if os.path.exists(vulnerabilities_file):
                            open_mode = "a"
                        else:
                            open_mode = "w"
                        with flock:
                            with open(
                                vulnerabilities_file, mode=open_mode, encoding="utf-8"
                            ) as portf:
                                portf.write(
                                    f"{ip} - {port} ({Network.getservice(port)})\n"
                                )

                    device = dev_ports.get(port)
                    if device:
                        local_dev.append(device)
                f.write(temp)

            if local_dev:
                devices.append(Counter(local_dev).most_common(1)[0][0])

            if hostname:
                with open(
                    os.path.join(dir_path, "domain.txt"), "w", encoding="utf-8"
                ) as f:
                    f.write(hostname)

            if mac_address:
                with open(
                    os.path.join(dir_path, "mac.txt"), "w", encoding="utf-8"
                ) as f:
                    f.write(mac_address)

        with lock:
            scanned_ips += 1

    except BaseException as e:
        logging.error(f"error on localscanner ({ip}): {e}")


def main():
    global loaded_ips, scanned_ips, timeouts, globalthreads, dumped_dns, devices, workth
    print(f"current network: {external_ip}")
    thh = threading.Thread(target=progress, daemon=True)
    thh.start()
    os.makedirs(dumpdir, exist_ok=True)
    os.makedirs(portsdir, exist_ok=True)

    handler = RotatingFileHandler(log_file, mode="w", maxBytes=10**6, backupCount=5)

    logging.basicConfig(
        handlers=[handler],
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    ip_ranges = Network.getranges()
    for addr in ip_ranges:
        if addr.endswith("/8"):
            globalthreads = min(_cpu_count * 64, 512)  # type: ignore

    with ThreadPoolExecutor(
        globalthreads, thread_name_prefix="global_scan"
    ) as main_executor:
        for addr_network in ip_ranges:
            network = ipaddress.IPv4Network(addr_network)
            for ip_obj in network.hosts():
                ip = ip_obj.compressed
                main_executor.submit(localscanner, ip)
                loaded_ips += 1

        main_executor.shutdown(wait=True)

    with open(os.path.join(dumpdir, "summary.txt"), "w", encoding="utf-8") as summary:
        summary.write(f"total time: {time.time() - start_time:.2f} seconds\n")
        summary.write(f"total loaded IPs: {loaded_ips}\n")
        summary.write(f"total scanned IPs: {scanned_ips}\n")

        if timeouts:
            avg_timeout = sum(timeouts) / len(timeouts)
            summary.write(f"average connection timeout: {avg_timeout}\n")
        else:
            summary.write("average connection timeout: N/A\n")

    mac_path = os.path.join(dumpdir, "mac_addresses.txt")
    mac_exists = os.path.exists(mac_path)

    dns_path = os.path.join(dumpdir, "dumped_dns.txt")
    dns_exists = os.path.exists(dns_path)

    with open(mac_path, "r+" if mac_exists else "w", encoding="utf-8") as macf:
        if not mac_exists:
            for ip, mac in mac_addresses.items():
                macf.write(f"{ip}: {mac}\n")

        else:
            f_dat = macf.read()
            for ip, mac in mac_addresses.items():
                t_dat = f"{ip}: {mac}\n"
                if not t_dat in f_dat:
                    macf.write(t_dat)

    with open(dns_path, "r+" if dns_exists else "w", encoding="utf-8") as dnsf:
        if not dns_exists:
            for ip, domain in dumped_dns.items():
                dnsf.write(f"{ip}: {domain}\n")

        else:
            f_dat = dnsf.read()
            for ip, domain in dumped_dns.items():
                t_dat = f"{ip}: {domain}\n"
                if not t_dat in f_dat:
                    dnsf.write(t_dat)

    with open(os.path.join(dumpdir, "ip_ranges.txt"), "w", encoding="utf-8") as rangef:
        rangef.write("\n".join(ip_ranges))

    device_stats = {}

    for device in devices:
        if device in device_stats:
            device_stats[device] += 1
        else:
            device_stats[device] = 1

    with open(
        os.path.join(dumpdir, "device_statistics.txt"), "w", encoding="utf-8"
    ) as f:
        for device, count in device_stats.items():
            f.write(f"{device}: {count}\n")

    workth = False
    thh.join()


if __name__ == "__main__":
    main()
