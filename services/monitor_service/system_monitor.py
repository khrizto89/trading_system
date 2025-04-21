# Monitoreo del sistema

import psutil
import torch
import threading
import time
from datetime import datetime

class SystemMonitor:
    def __init__(self, notification_service, log_file="system_metrics.log"):
        """
        Initialize the system monitor.
        :param notification_service: Service for sending notifications.
        :param log_file: File to log system metrics.
        """
        self.notification_service = notification_service
        self.log_file = log_file
        self.metrics_history = []
        self.lock = threading.Lock()
        self.running = False

    def start_monitoring(self, interval=5):
        """
        Start monitoring system resources.
        :param interval: Interval in seconds between checks.
        """
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, args=(interval,), daemon=True)
        self.thread.start()

    def stop_monitoring(self):
        """Stop monitoring system resources."""
        self.running = False
        if self.thread.is_alive():
            self.thread.join()

    def _monitor_loop(self, interval):
        """Main monitoring loop."""
        while self.running:
            metrics = self._collect_metrics()
            self._log_metrics(metrics)
            self._detect_anomalies(metrics)
            time.sleep(interval)

    def _collect_metrics(self):
        """Collect system metrics."""
        metrics = {
            "timestamp": datetime.now(),
            "cpu_usage": psutil.cpu_percent(),
            "memory_usage": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent,
            "network_io": psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv,
            "gpu_usage": torch.cuda.memory_allocated() / 1e6 if torch.cuda.is_available() else 0,
            "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "N/A"
        }
        with self.lock:
            self.metrics_history.append(metrics)
        return metrics

    def _log_metrics(self, metrics):
        """Log metrics to a file."""
        with open(self.log_file, "a") as f:
            f.write(f"{metrics}\n")

    def _detect_anomalies(self, metrics):
        """Detect anomalies in system metrics."""
        if metrics["cpu_usage"] > 90:
            self.notification_service.send("High CPU usage detected!")
        if metrics["memory_usage"] > 90:
            self.notification_service.send("High memory usage detected!")
        if metrics["disk_usage"] > 90:
            self.notification_service.send("High disk usage detected!")
        if metrics["gpu_usage"] > 90:
            self.notification_service.send("High GPU memory usage detected!")

    def get_metrics_history(self):
        """Get historical metrics."""
        with self.lock:
            return list(self.metrics_history)

    def healthcheck(self):
        """Perform health checks for all services."""
        health_status = {
            "cpu": psutil.cpu_percent() < 90,
            "memory": psutil.virtual_memory().percent < 90,
            "disk": psutil.disk_usage('/').percent < 90,
            "gpu": (torch.cuda.memory_allocated() / 1e6 if torch.cuda.is_available() else 0) < 90
        }
        return health_status

    def auto_recovery(self):
        """Apply auto-recovery policies for critical issues."""
        health_status = self.healthcheck()
        if not health_status["cpu"]:
            self.notification_service.send("Attempting to reduce CPU load...")
            # Placeholder for CPU recovery logic
        if not health_status["memory"]:
            self.notification_service.send("Attempting to free up memory...")
            # Placeholder for memory recovery logic
        if not health_status["disk"]:
            self.notification_service.send("Attempting to free up disk space...")
            # Placeholder for disk recovery logic
        if not health_status["gpu"]:
            self.notification_service.send("Attempting to optimize GPU usage...")
            # Placeholder for GPU recovery logic
