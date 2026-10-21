class SignatureDetector:
    def __init__(self):
        # Track connection attempts per source IP to detect Port Scans/Brute Force
        self.connection_attempts = {}
        self.alerted_flows = set() # <--- ADD THIS LINE

    def detect(self, features):
        """Rule-based detection. Returns an alert dict or None."""
        src_ip = features.get("src_ip")
        dst_port = features.get("dst_port")
        flow_key = features.get("flow_key")
        
        if not src_ip:
            return None

        # Rule 1: Simple Port Scan Detection
        if src_ip not in self.connection_attempts:
            self.connection_attempts[src_ip] = set()
            
        if dst_port:
            self.connection_attempts[src_ip].add(dst_port)
            
        if len(self.connection_attempts[src_ip]) > 15:
            self.connection_attempts[src_ip].clear() 
            return {
                "severity": "high",
                "alert_type": "port_scan",
                "description": f"Port scan detected from {src_ip}"
            }

        # Rule 2: Brute Force Detection
        if dst_port in [22, 3389] and features.get("packet_count", 0) > 20:
            if flow_key in self.alerted_flows: # <--- ADD THIS CHECK
                return None                    # <--- PREVENT DUPLICATES
                
            self.alerted_flows.add(flow_key)   # <--- REMEMBER THIS FLOW
            return {
                "severity": "critical",
                "alert_type": "brute_force",
                "description": f"Potential brute force on port {dst_port} from {src_ip}"
            }

        return None