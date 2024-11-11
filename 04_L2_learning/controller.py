#!/usr/bin/env python3
import argparse
import os
import sys
from time import sleep

import json
import grpc

from scapy.all import *

# Import P4Runtime lib
home_dir = os.path.expanduser('~')
p4_mininet_path = os.path.join(home_dir, 'p4-mininet')
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), p4_mininet_path))

import p4runtime_lib.bmv2
import p4runtime_lib.helper
from p4runtime_lib.simple_controller import *
from p4runtime_lib.convert import decodeNum
from p4runtime_lib.error_utils import printGrpcError
from p4runtime_lib.switch import ShutdownAllSwitchConnections


def writeBroadcastRule(p4info_helper, sw, ingress_port, mcast_grp):
    """
    :param p4info_helper: the P4Info helper
    :param sw: the P4Runtime switch connection
    :param ingress_port: the ingress port of the switch
    :param mcast_grp: the multicast group associated to the port
    """
    table_entry = p4info_helper.buildTableEntry(
        table_name = "MyIngress.mcast_grp",
        match_fields = {"smeta.ingress_port": ingress_port},
        action_name = "MyIngress.broadcast",
        action_params = {"mcast_grp": mcast_grp}
    )
    sw.WriteTableEntry(table_entry)
    print("Installed ingress broadcast rule (port %d to mcast grp %d) on %s"
          % (ingress_port, mcast_grp, sw.name))

def writeSMacRule(p4info_helper, sw, macSrcAddr):
    """
    :param p4info_helper: the P4Info helper
    :param sw: the P4Runtime switch connection
    :param macSrcAddr: the source MAC address to learn
    """
    # TODO: create table_entry for MyIngress.smac table 
    # ...
    
    try:
        sw.WriteTableEntry(table_entry)
        print("Installed ingress smac rule (stop learning from %s) on %s"
              % (macSrcAddr, sw.name))
    except grpc.RpcError as e:
        # printGrpcError(e)
        # Should be an "ALREADY_EXISTS" error, use MODIFY instead of INSERT
        # We ignore this error...
        pass

def writeDMacRule(p4info_helper, sw, macDstAddr, egress_port):
    """
    :param p4info_helper: the P4Info helper
    :param sw: the P4Runtime switch connection
    :param macDstAddr: the destination MAC address
    :param egress_port: the egress port to forward to
    """
    # TODO: create table_entry for MyIngress.dmac table 
    # ...
   
    try:
        sw.WriteTableEntry(table_entry)
        print("Installed ingress dmac rule (%s forward to %d) on %s"
              % (macDstAddr, egress_port, sw.name))
    except grpc.RpcError as e:
        # printGrpcError(e)
        # Should be an "ALREADY_EXISTS" error, use MODIFY instead of INSERT
        # We ignore this error...
        pass

def learn(p4info_helper, sw, mac_addr, ingress_port):
    # print("Learning mac %s on port %s" % (mac_addr, ingress_port))
    # TODO: call writeSMacRule and writeDMacRule
    # ...


# ================    
#  Main function 
# ================
def main(runtime_conf_file):
    
    with open(runtime_conf_file, 'r') as sw_conf_file:
        sw_conf = json_load_byteified(sw_conf_file)
    workdir = '.'
    try:
        check_switch_conf(sw_conf=sw_conf, workdir=workdir)
    except ConfException as e:
        error("While parsing input runtime configuration: %s" % str(e))
        return
    
    print('Using P4Info file %s' % sw_conf['p4info'])
    p4info_file_path = os.path.join(workdir, sw_conf['p4info'])
    print('Using BMv2 json file %s' % sw_conf['bmv2_json'])
    bmv2_file_path = os.path.join(workdir, sw_conf['bmv2_json'])
    
    # Instantiate a P4Runtime helper from the p4info file
    p4info_helper = p4runtime_lib.helper.P4InfoHelper(p4info_file_path)

    try:
        # Create a switch connection object for s1;
        # this is backed by a P4Runtime gRPC connection.
        # Also, dump all P4Runtime messages sent to switch to given txt files.
        sw = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s1',
            address='127.0.0.1:50051',
            device_id=0,
            proto_dump_file='logs/s1-p4runtime-requests.txt')

        # Send master arbitration update message to establish this controller as
        # master (required by P4Runtime before performing any other write operation)
        sw.MasterArbitrationUpdate()

        # Install the P4 program (bmv2_json_file_path) on the switch 
        sw.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                       bmv2_json_file_path=bmv2_file_path)
        print("Installed P4 Program using SetForwardingPipelineConfig on s1")

        # To add table, multicast groups and clone session entries,
        # we rely on p4runtime_lib.simple_controller
        
        # Add table entries if any
        if 'table_entries' in sw_conf:
            table_entries = sw_conf['table_entries']
            print("Inserting %d table entries..." % len(table_entries))
            for entry in table_entries:
                print(tableEntryToString(entry))
                validateTableEntry(entry, p4info_helper, runtime_json)
                insertTableEntry(sw, entry, p4info_helper)

        # Configure multicast groups if any
        if 'multicast_group_entries' in sw_conf:
            group_entries = sw_conf['multicast_group_entries']
            print("Inserting %d group entries..." % len(group_entries))
            for entry in group_entries:
                print(groupEntryToString(entry))
                insertMulticastGroupEntry(sw, entry, p4info_helper)

        # Configure mirrors if any
        if 'clone_session_entries' in sw_conf:
            clone_entries = sw_conf['clone_session_entries']
            print("Inserting %d clone entries..." % len(clone_entries))
            for entry in clone_entries:
                print(cloneEntryToString(entry))
                insertCloneGroupEntry(sw, entry, p4info_helper)


        # Install table entries in the mcast_grp table
        # Port i is associated to multicast group i
        # (note: we hard code the port numbers, not the best...)
        for i in [1, 2, 3, 4]:
            writeBroadcastRule(p4info_helper, sw, i, i)

        # Waiting for packetIn packets from the switch
        while True:
            packetin = sw.StreamMessageIn()
            if packetin.WhichOneof('update') == 'packet':
                print("Received Packet-in")
                raw_packet = packetin.packet.payload
                # print(packet)
                scapy_pkt = Ether(raw_packet)
                # scapy_pkt.show()
                ether_type = scapy_pkt.type
                eth_src = scapy_pkt.src
                # if packet is IPv4 or ARP
                if ether_type == 0x0800 or ether_type == 0x0806:
                    metadata = packetin.packet.metadata 
                    for meta in metadata:
                        id = meta.metadata_id 
                        value = meta.value
                        print("id " + str(id) + " value " + str(value))
                    print("*** Learning from %s on port %d ***" % (eth_src, decodeNum(value)))
                    learn(p4info_helper, sw, eth_src, decodeNum(value))
                else:
                    print("Packet type not implemented")

    except KeyboardInterrupt:
        print(" Shutting down.")
    except grpc.RpcError as e:
        printGrpcError(e)

    ShutdownAllSwitchConnections()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='P4Runtime Controller')
    parser.add_argument("-c", '--runtime-conf-file',
                        help="path to input runtime configuration file (JSON)",
                        type=str, action="store", required=True)
    args = parser.parse_args()

    if not os.path.exists(args.runtime_conf_file):
        parser.print_help()
        print("\nRuntime conf file not found: %s\n" % args.runtime_conf_file)
        parser.exit(1)
    
    main(args.runtime_conf_file)
