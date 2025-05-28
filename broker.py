import zmq
import threading
import time
from utils.constants import (
    BROKER_IP,
    AUDIO_XSUB_PORT, AUDIO_XPUB_PORT,
    VIDEO_XSUB_PORT, VIDEO_XPUB_PORT,
    TEXT_XSUB_PORT, TEXT_XPUB_PORT
)

class MessageBroker:
    def __init__(self, ip=BROKER_IP,
                 audio_xsub_port=AUDIO_XSUB_PORT, audio_xpub_port=AUDIO_XPUB_PORT,
                 video_xsub_port=VIDEO_XSUB_PORT, video_xpub_port=VIDEO_XPUB_PORT,
                 text_xsub_port=TEXT_XSUB_PORT, text_xpub_port=TEXT_XPUB_PORT):
        self.ip = ip
        self.audio_xsub_port = audio_xsub_port
        self.audio_xpub_port = audio_xpub_port
        self.video_xsub_port = video_xsub_port
        self.video_xpub_port = video_xpub_port
        self.text_xsub_port = text_xsub_port
        self.text_xpub_port = text_xpub_port
        self.context = zmq.Context()

        print(f"Iniciando broker em {self.ip}...")

    def _start_forwarder(self, xsub_port, xpub_port, data_type):
        """Função genérica para iniciar um forwarder XSUB/XPUB."""
        frontend = self.context.socket(zmq.XSUB)
        frontend.bind(f"tcp://*:{xsub_port}") # Agora usa a porta XSUB dedicada

        backend = self.context.socket(zmq.XPUB)
        backend.bind(f"tcp://*:{xpub_port}") # Agora usa a porta XPUB dedicada

        print(f"Forwarder {data_type} iniciado: XSUB em porta {xsub_port}, XPUB em porta {xpub_port}")

        zmq.proxy(frontend, backend)

    def start(self):
        """Inicia os forwarders para áudio, vídeo e texto."""
        audio_thread = threading.Thread(target=self._start_forwarder, args=(self.audio_xsub_port, self.audio_xpub_port, "Áudio"))
        video_thread = threading.Thread(target=self._start_forwarder, args=(self.video_xsub_port, self.video_xpub_port, "Vídeo"))
        text_thread = threading.Thread(target=self._start_forwarder, args=(self.text_xsub_port, self.text_xpub_port, "Texto"))

        audio_thread.daemon = True
        video_thread.daemon = True
        text_thread.daemon = True

        audio_thread.start()
        video_thread.start()
        text_thread.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nBroker encerrado.")
            self.context.term()

if __name__ == "__main__":
    broker = MessageBroker()
    broker.start()