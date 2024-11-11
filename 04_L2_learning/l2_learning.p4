/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

#define PKT_INSTANCE_TYPE_NORMAL 0
#define PKT_INSTANCE_TYPE_INGRESS_CLONE 1

/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/

// TODO: define ethernet_t header --> copy from previous exercise 


// TODO: define a new packet_in_t header which includes an ingress_port field
// annotate with @controller_header("packet_in")

// TODO: define struct headers


struct metadata {
    // TODO: add an ingress_port field in the user's metadata
    // annotate with @field_list(1)

}



/*************************************************************************
************************* P A R S E R  ***********************************
*************************************************************************/

parser MyParser(packet_in packet,
                out headers hdr,
                inout metadata meta,
                inout standard_metadata_t smeta) {

    state start {
        // TODO: parse ethernet header --> copy from previous exercise

    }

}

/*************************************************************************
************   C H E C K S U M    V E R I F I C A T I O N   **************
*************************************************************************/

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {
    apply { }
}


/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   ********************
*************************************************************************/

control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t smeta) {

    // TODO:
    // - copy forward and broadcast actions from previous exercise
    // - copy dmac and mcast_grp tables from previous exercise


    // TODO: add mac_learn action, saving ingress_port and cloning packet


    // TODO: add smac table to learn from source MAC address


    apply {
        // TODO: apply smac table

        // TODO (copy from previous exercise)
        // -> apply mcast_grp table if no hit on dmac table

    }

}

/*************************************************************************
*****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t smeta) {
    apply {
        // TODO: if packet is an ingress clone, add cpu header
        // (setValid and init ingress_port) 
     
     
    }
}

/*************************************************************************
*************   C H E C K S U M    C O M P U T A T I O N   ***************
*************************************************************************/

control MyComputeChecksum(inout headers  hdr, inout metadata meta) {
    apply { }
}

/*************************************************************************
***********************  D E P A R S E R  ********************************
*************************************************************************/

control MyDeparser(packet_out packet, in headers hdr) {
    apply {
        // TODO: deparse cpu and ethernet header

    }
}

/*************************************************************************
*************************  S W I T C H  **********************************
*************************************************************************/

V1Switch(
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
) main;
