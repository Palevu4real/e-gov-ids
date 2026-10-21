from scapy.all import Ether, IP, TCP, wrpcap
import time

def create_attack_pcap():
    packets = []
    base_time = time.time()

    # 1. Normal traffic (10 HTTP requests)
    for i in range(10):
        pkt = Ether()/IP(src="192.168.1.50", dst="10.0.0.5")/TCP(sport=50000+i, dport=80, flags="S")
        pkt.time = base_time + i
        packets.append(pkt)

    # 2. Port Scan Attack (20 packets hitting different ports from one IP)
    for port in range(1, 25):
        pkt = Ether()/IP(src="203.0.113.66", dst="10.0.0.5")/TCP(sport=12345, dport=port, flags="S")
        pkt.time = base_time + 20 + port
        packets.append(pkt)

    # 3. Brute Force Attack (50 SSH packets to port 22 from one IP)
    for i in range(50):
        pkt = Ether()/IP(src="198.51.100.22", dst="10.0.0.5")/TCP(sport=40000+i, dport=22, flags="S")
        pkt.time = base_time + 50 + i
        packets.append(pkt)

    # 4. Anomaly/Data Exfiltration (huge packets)
    for i in range(5):
        pkt = Ether()/IP(src="192.168.1.99", dst="203.0.113.100")/TCP(sport=44444, dport=443, flags="A")
        pkt = pkt / ("X" * 1400)
        pkt.time = base_time + 100 + i
        packets.append(pkt)

    wrpcap("/app/pcaps/sample.pcap", packets)
    print("✅ Created /app/pcaps/sample.pcap with simulated attacks!")

if __name__ == "__main__":
    create_attack_pcap()