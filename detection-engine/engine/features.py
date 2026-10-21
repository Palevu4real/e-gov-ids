from collections import defaultdict
import time

class FlowTracker:
    def __init__(self):
        # A simple in-memory tracker for active flows
        self.flows = defaultdict(lambda: {"packets": 0, "bytes": 0, "start_time": time.time()})

    def process_packet(self, packet):
        """Extract features from a Scapy packet."""
        if not packet.haslayer('IP'):
            return None
            
        src_ip = packet['IP'].src
        dst_ip = packet['IP'].dst
        proto = packet['IP'].proto
        length = len(packet)
        
        # Identify destination port if TCP/UDP
        dst_port = None
        if packet.haslayer('TCP'):
            dst_port = packet['TCP'].dport
        elif packet.haslayer('UDP'):
            dst_port = packet['UDP'].dport

        flow_key = f"{src_ip}:{dst_ip}:{dst_port}"
        flow = self.flows[flow_key]
        
        flow["packets"] += 1
        flow["bytes"] += length
        flow["last_seen"] = time.time()
        duration = flow["last_seen"] - flow["start_time"]

        return {
            "src_ip": src_ip,
            "dst_ip": dst_ip,
            "dst_port": dst_port,
            "protocol": proto,
            "packet_length": length,
            "packet_count": flow["packets"],
            "byte_count": flow["bytes"],
            "duration": duration,
            "flow_key": flow_key
        }