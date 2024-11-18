#!/usr/bin/env python3
import sys
import socket
import time

from scapy.all import sendp, get_if_list, get_if_hwaddr
from scapy.all import Ether, IP, TCP

def get_if():
    ifs=get_if_list()
    iface=None # "h1-eth0"
    for i in get_if_list():
        if "eth0" in i:
            iface=i
            break
    if not iface:
        print("Cannot find eth0 interface")
        exit(1)
    return iface

def main():

    if len(sys.argv) != 4:
        print('Usage: send.py <destination> <num_packets> <sleep_time_ms_between_packets>')
        exit(1)

    addr = socket.gethostbyname(sys.argv[1])
    iface = get_if()

    print("Sending on interface %s to %s" % (iface, str(addr)))
    print('...')
    for _ in range(int(sys.argv[2])):
        pkt = Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff')
        # create a TCP SYN segment with same src and dst ports
        # (same flow, but possibly different flowlets according to sleep time between packets)
        pkt = pkt / IP(dst=addr) / TCP(sport=60000, dport=60001, flags='S')
        sendp(pkt, iface=iface, verbose=False)
        time.sleep(float(sys.argv[3]) * 10**-3) # time.sleep is in seconds
    print('Done.')

if __name__ == '__main__':
    main()
