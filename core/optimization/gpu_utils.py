# Utilidades para optimización de GPU

import torch
import tensorflow as tf
import pynvml

class GPUUtils:
    """Utilidades para optimización de GPU en RTX 4070Ti."""

    def __init__(self):
        pynvml.nvmlInit()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def configure_memory(self, memory_fraction=0.8):
        """Configura el uso de memoria para TensorFlow."""
        gpus = tf.config.experimental.list_physical_devices('GPU')
        if gpus:
            try:
                for gpu in gpus:
                    tf.config.experimental.set_memory_growth(gpu, True)
                    tf.config.experimental.set_virtual_device_configuration(
                        gpu,
                        [tf.config.experimental.VirtualDeviceConfiguration(memory_limit=int(memory_fraction * pynvml.nvmlDeviceGetMemoryInfo(pynvml.nvmlDeviceGetHandleByIndex(0)).total))]
                    )
            except RuntimeError as e:
                print(f"Error configurando memoria: {e}")

    def optimize_model_pytorch(self, model):
        """Optimiza un modelo PyTorch para GPU."""
        model = model.to(self.device)
        model = torch.compile(model)  # Requiere PyTorch 2.0+
        return model

    def optimize_model_tf(self, model):
        """Optimiza un modelo TensorFlow para GPU."""
        options = tf.saved_model.LoadOptions(experimental_io_device="/job:localhost/replica:0/task:0/device:GPU:0")
        return tf.saved_model.load(model, options=options)

    def manage_cuda_streams(self, streams):
        """Gestiona CUDA streams para operaciones paralelas."""
        cuda_streams = [torch.cuda.Stream() for _ in range(streams)]
        return cuda_streams

    def monitor_gpu(self):
        """Monitorea temperatura, uso y rendimiento de la GPU."""
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
        utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
        memory = pynvml.nvmlDeviceGetMemoryInfo(handle)
        return {
            "temperature": temp,
            "gpu_utilization": utilization.gpu,
            "memory_utilization": utilization.memory,
            "memory_used": memory.used,
            "memory_total": memory.total
        }

    def optimize_inference_throughput(self, model, batch_size):
        """Optimiza throughput en inferencia ajustando el tamaño de batch."""
        if isinstance(model, torch.nn.Module):
            model.eval()
            with torch.no_grad():
                dummy_input = torch.randn(batch_size, *model.input_shape).to(self.device)
                model(dummy_input)
        elif isinstance(model, tf.keras.Model):
            dummy_input = tf.random.normal([batch_size, *model.input_shape[1:]])
            model.predict(dummy_input)

    def cleanup(self):
        """Libera recursos de GPU."""
        torch.cuda.empty_cache()
        pynvml.nvmlShutdown()
