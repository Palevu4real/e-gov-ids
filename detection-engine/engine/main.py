import asyncio
import logging
import os
import time

from scapy.all import rdpcap

from engine.features import FlowTracker
from engine.detectors.signature import SignatureDetector
from engine.detectors.anomaly import AnomalyDetector
from engine.publisher import KafkaPublisher

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("detection-engine")

# Files already processed (path, mtime). Prevents reprocessing in a loop
# if the rename to ".done" fails (e.g. read-only volume).
_processed = set()


class AlertDeduper:
    """Allow only one alert per (alert_type, source_ip) within a cooldown window."""

    def __init__(self, cooldown: int = 60):
        self.cooldown = cooldown
        self._last = {}

    def allow(self, alert_type: str, src_ip: str) -> bool:
        now = time.monotonic()
        key = (alert_type, src_ip)
        last = self._last.get(key)
        if last is not None and (now - last) < self.cooldown:
            return False
        self._last[key] = now
        return True


async def emit_alert(label, detector_alert, features, publisher, deduper):
    alert = {
        "timestamp": time.time(),
        "source_ip": features["src_ip"],
        "dest_ip": features["dst_ip"],
        **detector_alert,
    }
    if not deduper.allow(alert["alert_type"], alert["source_ip"]):
        return
    log.warning(f"🚨 {label} ALERT: {alert['alert_type']} from {alert['source_ip']}")
    await publisher.publish(alert)


async def process_pcap(pcap_file, publisher):
    log.info(f"Loading packets from {pcap_file}...")
    try:
        packets = rdpcap(pcap_file)
    except Exception as e:
        log.error(f"Failed to read pcap: {e!r}")
        return

    tracker = FlowTracker()
    sig_detector = SignatureDetector()
    anomaly_detector = AnomalyDetector()
    # New deduper per file: each PCAP yields one alert per type/IP
    deduper = AlertDeduper(cooldown=int(os.getenv("ALERT_COOLDOWN", "60")))

    log.info(f"Processing {len(packets)} packets...")

    for packet in packets:
        features = tracker.process_packet(packet)
        if not features:
            continue

        # 1. Signature detector
        sig_alert = sig_detector.detect(features)
        if sig_alert:
            await emit_alert("SIGNATURE", sig_alert, features, publisher, deduper)

        # 2. Anomaly detector
        anom_alert = anomaly_detector.detect(features)
        if anom_alert:
            await emit_alert("ANOMALY", anom_alert, features, publisher, deduper)

        # Slight sleep to simulate real-time traffic
        await asyncio.sleep(0.01)

    log.info("Finished processing PCAP file.")


def mark_done(pcap_file, mtime):
    """Rename to .done; if that fails, remember the file so it isn't reprocessed."""
    _processed.add((pcap_file, mtime))
    try:
        os.replace(pcap_file, pcap_file + ".done")
        log.info(f"Renamed {pcap_file} -> {pcap_file}.done")
    except OSError as e:
        log.error(
            f"Could not rename {pcap_file} ({e!r}). "
            "Is the /pcaps volume mounted read-only? "
            "Will skip this file until it changes."
        )


async def run():
    log.info("Detection engine starting...")
    publisher = KafkaPublisher()
    await publisher.start()
    log.info("Kafka Producer started.")

    pcap_file = os.getenv("PCAP_FILE", "/pcaps/sample.pcap")
    log.info(f"Watching for {pcap_file} ...")

    # Keep the engine running forever; never let one bad file kill it
    while True:
        try:
            if os.path.exists(pcap_file):
                mtime = os.path.getmtime(pcap_file)
                if (pcap_file, mtime) not in _processed:
                    await process_pcap(pcap_file, publisher)
                    mark_done(pcap_file, mtime)
        except Exception as e:
            log.error(f"Unexpected error in main loop: {e!r}")

        await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(run())