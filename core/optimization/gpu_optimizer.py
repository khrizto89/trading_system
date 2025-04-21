# Optimizaciones para GPU (RTX 4070Ti)

import torch
import torch.backends.cudnn as cudnn
import time
import numpy as np
from torch.cuda.amp import autocast, GradScaler
import tensorrt as trt

class GPUOptimizer:
    def __init__(self, device="cuda"):
        """
        Initialize the GPU optimizer.
        :param device: Device to use ('cuda' or 'cpu').
        """
        self.device = torch.device(device if torch.cuda.is_available() else "cpu")
        self.scaler = GradScaler()  # For mixed precision training
        cudnn.benchmark = True  # Enable cuDNN auto-tuner for better performance

    def optimize_model(self, model):
        """
        Optimize the model for GPU inference using TensorRT.
        :param model: PyTorch model to optimize.
        :return: Optimized model.
        """
        model = model.to(self.device)
        model.eval()
        # Placeholder for TensorRT optimization (requires ONNX export)
        return model

    def train_with_mixed_precision(self, model, train_loader, optimizer, criterion, epochs=10):
        """
        Train the model using mixed precision (FP16/FP32).
        :param model: PyTorch model.
        :param train_loader: DataLoader for training data.
        :param optimizer: Optimizer for training.
        :param criterion: Loss function.
        :param epochs: Number of epochs.
        """
        model = model.to(self.device)
        for epoch in range(epochs):
            model.train()
            epoch_loss = 0.0
            start_time = time.time()

            for inputs, targets in train_loader:
                inputs, targets = inputs.to(self.device), targets.to(self.device)

                with autocast():  # Mixed precision
                    outputs = model(inputs)
                    loss = criterion(outputs, targets)

                self.scaler.scale(loss).backward()
                self.scaler.step(optimizer)
                self.scaler.update()
                optimizer.zero_grad()

                epoch_loss += loss.item()

            end_time = time.time()
            print(f"Epoch {epoch+1}/{epochs}, Loss: {epoch_loss:.4f}, Time: {end_time - start_time:.2f}s")

    def batch_inference(self, model, data_loader, batch_size=32):
        """
        Perform batch inference to maximize throughput.
        :param model: PyTorch model.
        :param data_loader: DataLoader for inference data.
        :param batch_size: Batch size for inference.
        :return: Inference results.
        """
        model = model.to(self.device)
        model.eval()
        results = []

        with torch.no_grad():
            for inputs in data_loader:
                inputs = inputs.to(self.device)
                with autocast():  # Mixed precision
                    outputs = model(inputs)
                results.append(outputs.cpu().numpy())

        return np.concatenate(results, axis=0)

    def monitor_performance(self):
        """
        Monitor GPU performance (latency, throughput, utilization).
        """
        if not torch.cuda.is_available():
            print("CUDA is not available.")
            return

        print(f"GPU Name: {torch.cuda.get_device_name(0)}")
        print(f"Memory Allocated: {torch.cuda.memory_allocated() / 1e6:.2f} MB")
        print(f"Memory Cached: {torch.cuda.memory_reserved() / 1e6:.2f} MB")
        print(f"GPU Utilization: {torch.cuda.utilization(0)}%")

    def adjust_parameters(self, model, data_loader, max_memory_usage=0.8):
        """
        Adjust batch size or model parameters to avoid OOM errors.
        :param model: PyTorch model.
        :param data_loader: DataLoader for data.
        :param max_memory_usage: Maximum GPU memory usage allowed (fraction).
        :return: Adjusted batch size.
        """
        batch_size = data_loader.batch_size
        while True:
            try:
                self.batch_inference(model, data_loader, batch_size=batch_size)
                break
            except RuntimeError as e:
                if "out of memory" in str(e):
                    batch_size = max(1, batch_size // 2)
                    print(f"Reducing batch size to {batch_size} to avoid OOM.")
                else:
                    raise e
        return batch_size

    def benchmark(self, model, data_loader):
        """
        Benchmark the model for latency and throughput.
        :param model: PyTorch model.
        :param data_loader: DataLoader for inference data.
        """
        model = model.to(self.device)
        model.eval()
        start_time = time.time()

        with torch.no_grad():
            for inputs in data_loader:
                inputs = inputs.to(self.device)
                with autocast():  # Mixed precision
                    _ = model(inputs)

        end_time = time.time()
        latency = (end_time - start_time) / len(data_loader)
        throughput = len(data_loader.dataset) / (end_time - start_time)

        print(f"Latency: {latency:.4f}s per batch")
        print(f"Throughput: {throughput:.2f} samples/second")
