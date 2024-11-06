/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/

struct metadata {
    /* empty */
}

/* TODO: define ethernet_t header and headers struct */
/* --> copy from previous exercise */



/*************************************************************************
************************* P A R S E R  ***********************************
*************************************************************************/

parser MyParser(packet_in packet,
                out headers hdr,
                inout metadata meta,
                inout standard_metadata_t smeta) {

    state start {
        /* TODO: parse ethernet header --> copy from previous exercise */

        transition accept;
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

    /* TODO: define a forward action to set smeta.egress_spec */
    /* --> copy from previous exercise */

    /* New TODO v1: add a broadcast action to modify smeta.mcast_grp */

    /* New TODO v2: modify the broadcast action, adding a parameter */


    /* TODO: define a dmac table that can trigger the previous actions */
    /* --> copy from previous exercise */
    /* New TODO v1: set default action to broadcast */
    /* New TODO v2: set default action to NoAction */


    /* New TODO v2: define an mcast_grp table */
 

    apply {
        /* TODO: apply dmac table --> copy from previous exercise */
 
        /* New TODO v2: apply mcast_grp table if no hit on dmac table */

    }

}

/*************************************************************************
*****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {
    apply { }
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
        /* TODO: deparse ethernet header --> copy from previous exercise */

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
