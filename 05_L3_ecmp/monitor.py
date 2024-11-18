#!/usr/bin/env python3
import argparse
import os
import sys
from time import sleep

import json
import grpc

# To convert bytes to an IP address
import socket, struct

# Import P4Runtime lib
home_dir = os.path.expanduser('~')
p4_mininet_path = os.path.join(home_dir, 'p4-mininet')
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), p4_mininet_path))

import p4runtime_lib.bmv2
import p4runtime_lib.helper
from p4runtime_lib.error_utils import printGrpcError
from p4runtime_lib.switch import ShutdownAllSwitchConnections

def bytesToIPv4Addr(bytes):
    int_val = int.from_bytes(bytes, 'big')
    return socket.inet_ntoa(struct.pack('>L', int_val))

def printDirectCounters(p4info_helper, sw, table_name):
    """
    Reads the direct counters at the specified table from the switch.
    :param p4info_helper: the P4Info helper
    :param sw:  the switch connection
    :param table_name: the name of the table to read the counters from
    """
    for response in sw.ReadDirectCounters(p4info_helper.get_tables_id(table_name)):
        for entity in response.entities:
            counter = entity.direct_counter_entry
            for m in entity.direct_counter_entry.table_entry.match:
                match_value = p4info_helper.get_match_field_value(m)
                print("%s %s, dstAddr %s/%d: %d packets (%d bytes)" % (
                    sw.name, table_name, bytesToIPv4Addr(match_value[0]), match_value[1],
                    counter.data.packet_count, counter.data.byte_count )
                )

# ================    
#  Main function 
# ================
def main(p4info_file):
    
    print('Using P4Info file %s' % p4info_file)    
    # Instantiate a P4Runtime helper from the p4info file
    p4info_helper = p4runtime_lib.helper.P4InfoHelper(p4info_file)
    
    # Switches to monitor (name, gRPC port, device id)
    sw_list = [ ('s10', 50053, 2), ('s11', 50054, 3), ('s12', 50055, 4), ('s13', 50056, 5) ]
    sw_connections = []

    try:                    
        # Create a switch connection object for each switch
        for i, val in enumerate(sw_list):
            sw_connections.append(
                p4runtime_lib.bmv2.Bmv2SwitchConnection(
                    name = val[0],
                    address = '127.0.0.1:'+str(val[1]),
                    device_id = val[2])
            )
    
        # Print the ipv4_lpm direct counters every 5 seconds
        while True:
            print('\n========== Reading direct counters ==========')
            for sw in sw_connections:
                printDirectCounters(p4info_helper, sw, "MyIngress.ipv4_lpm")
                print('')
            sleep(5)
    
    except KeyboardInterrupt:
        print(" Shutting down.")
    except grpc.RpcError as e:
        printGrpcError(e)

    ShutdownAllSwitchConnections()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='P4Runtime Monitor')
    parser.add_argument('--p4info', help='p4info proto in text format from p4c',
                        type=str, action="store", required=False,
                        default='./build/ecmp.p4.p4info.txt')
    args = parser.parse_args()
    main(args.p4info)
