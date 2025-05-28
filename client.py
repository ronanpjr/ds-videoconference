import zmq
import threading
import pyaudio
import cv2
import numpy as np
import sys
import time
from utils.constants import (
    BROKER_IP,
    AUDIO_XSUB_PORT, AUDIO_XPUB_PORT,
    VIDEO_XSUB_PORT, VIDEO_XPUB_PORT,
    TEXT_XSUB_PORT, TEXT_XPUB_PORT,
    AUDIO_CHUNK_SIZE, VIDEO_FRAME_WIDTH, VIDEO_FRAME_HEIGHT, FPS,
    TOPIC_AUDIO, TOPIC_VIDEO, TOPIC_TEXT, CLIENT_ID
)

class VideoConferenceClient:
    def __init__(self, client_id, broker_ip=BROKER_IP,
                 audio_pub_port=AUDIO_XSUB_PORT, audio_sub_port=AUDIO_XPUB_PORT,
                 video_pub_port=VIDEO_XSUB_PORT, video_sub_port=VIDEO_XPUB_PORT,
                 text_pub_port=TEXT_XSUB_PORT, text_sub_port=TEXT_XPUB_PORT):

        self.client_id = client_id
        globals()['CLIENT_ID'] = client_id # Necessário para o CLIENT_ID global

        self.broker_ip = broker_ip
        self.audio_pub_port = audio_pub_port
        self.audio_sub_port = audio_sub_port
        self.video_pub_port = video_pub_port
        self.video_sub_port = video_sub_port
        self.text_pub_port = text_pub_port
        self.text_sub_port = text_sub_port

        self.context = zmq.Context()

        # Sockets de Publicação (conectam nas portas XSUB do broker)
        self.audio_pub_socket = self.context.socket(zmq.PUB)
        self.audio_pub_socket.connect(f"tcp://{self.broker_ip}:{self.audio_pub_port}")

        self.video_pub_socket = self.context.socket(zmq.PUB)
        self.video_pub_socket.connect(f"tcp://{self.broker_ip}:{self.video_pub_port}")

        self.text_pub_socket = self.context.socket(zmq.PUB)
        self.text_pub_socket.connect(f"tcp://{self.broker_ip}:{self.text_pub_port}")

        # Sockets de Assinatura (conectam nas portas XPUB do broker)
        self.audio_sub_socket = self.context.socket(zmq.SUB)
        self.audio_sub_socket.connect(f"tcp://{self.broker_ip}:{self.audio_sub_port}")
        self.audio_sub_socket.setsockopt_string(zmq.SUBSCRIBE, TOPIC_AUDIO.decode('utf-8'))

        self.video_sub_socket = self.context.socket(zmq.SUB)
        self.video_sub_socket.connect(f"tcp://{self.broker_ip}:{self.video_sub_port}")
        self.video_sub_socket.setsockopt_string(zmq.SUBSCRIBE, TOPIC_VIDEO.decode('utf-8'))

        self.text_sub_socket = self.context.socket(zmq.SUB)
        self.text_sub_socket.connect(f"tcp://{self.broker_ip}:{self.text_sub_port}")
        self.text_sub_socket.setsockopt_string(zmq.SUBSCRIBE, TOPIC_TEXT.decode('utf-8'))

        
        self.pyaudio_instance = pyaudio.PyAudio()
        self.audio_stream = None
        self.video_capture = None

        self.running = True

        print(f"Cliente {self.client_id} conectado ao broker em {self.broker_ip}")

    def _send_audio(self):
        """Captura e envia áudio."""
        self.audio_stream = self.pyaudio_instance.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=44100,
            input=True,
            frames_per_buffer=AUDIO_CHUNK_SIZE
        )
        print("Iniciando envio de áudio...")
        while self.running:
            try:
                audio_data = self.audio_stream.read(AUDIO_CHUNK_SIZE, exception_on_overflow=False)
                # Adiciona o ID do cliente ao início da mensagem para evitar eco
                self.audio_pub_socket.send_multipart([TOPIC_AUDIO, self.client_id.encode('utf-8'), audio_data])
            except Exception as e:
                print(f"Erro ao enviar áudio: {e}")
                break
        self.audio_stream.stop_stream()
        self.audio_stream.close()

    def _receive_audio(self):
        """Recebe e reproduz áudio."""
        output_stream = self.pyaudio_instance.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=44100,
            output=True
        )
        print("Iniciando recebimento de áudio...")
        while self.running:
            try:
                # Recebe o tópico, ID do remetente e dados de áudio
                topic, sender_id, audio_data = self.audio_sub_socket.recv_multipart()
                # Não reproduz o próprio áudio
                if sender_id.decode('utf-8') != self.client_id:
                    output_stream.write(audio_data)
            except zmq.Again:
                pass  # No messages yet
            except Exception as e:
                print(f"Erro ao receber áudio: {e}")
                break
        output_stream.stop_stream()
        output_stream.close()

    def _send_video(self):
        """Captura e envia vídeo."""
        self.video_capture = cv2.VideoCapture(0) # 0 para a webcam padrão
        self.video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, VIDEO_FRAME_WIDTH)
        self.video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, VIDEO_FRAME_HEIGHT)
        self.video_capture.set(cv2.CAP_PROP_FPS, FPS)

        print("Iniciando envio de vídeo...")
        while self.running:
            ret, frame = self.video_capture.read()
            if not ret:
                print("Falha ao capturar frame da webcam.")
                break

            # Redimensiona o frame para consistência (opcional, mas recomendado)
            frame_resized = cv2.resize(frame, (VIDEO_FRAME_WIDTH, VIDEO_FRAME_HEIGHT))
            
            # Codifica o frame para JPG para reduzir o tamanho
            _, buffer = cv2.imencode('.jpg', frame_resized)
            video_data = buffer.tobytes()

            try:
                # Adiciona o ID do cliente ao início da mensagem
                self.video_pub_socket.send_multipart([TOPIC_VIDEO, self.client_id.encode('utf-8'), video_data])
            except Exception as e:
                print(f"Erro ao enviar vídeo: {e}")
                break
            time.sleep(1 / FPS) # Controla a taxa de quadros
        self.video_capture.release()

    def _receive_video(self):
        """Recebe e exibe vídeo."""
        print("Iniciando recebimento de vídeo...")
        cv2.namedWindow(f"Video {self.client_id}", cv2.WINDOW_NORMAL)
        cv2.resizeWindow(f"Video {self.client_id}", VIDEO_FRAME_WIDTH, VIDEO_FRAME_HEIGHT)

        while self.running:
            try:
                # Recebe o tópico, ID do remetente e dados de vídeo
                topic, sender_id, video_data = self.video_sub_socket.recv_multipart()
                
                # Não exibe o próprio vídeo
                if sender_id.decode('utf-8') != self.client_id:
                    # Decodifica o frame JPG
                    nparr = np.frombuffer(video_data, np.uint8)
                    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    if frame is not None:
                        cv2.imshow(f"Video de {sender_id.decode('utf-8')}", frame)
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            self.running = False
            except zmq.Again:
                pass  # No messages yet
            except Exception as e:
                print(f"Erro ao receber vídeo: {e}")
                break
        cv2.destroyAllWindows()

    def _send_text(self):
        """Permite ao usuário digitar e enviar texto."""
        print("Digite suas mensagens (digite 'sair' para parar o chat):")
        while self.running:
            try:
                message = input("")
                if message.lower() == 'sair':
                    self.running = False
                    break
                
                # Adiciona o ID do cliente ao início da mensagem
                full_message = f"[{self.client_id}]: {message}"
                self.text_pub_socket.send_multipart([TOPIC_TEXT, self.client_id.encode('utf-8'), full_message.encode('utf-8')])
            except Exception as e:
                print(f"Erro ao enviar texto: {e}")
                break

    def _receive_text(self):
        """Recebe e exibe mensagens de texto."""
        print("Iniciando recebimento de texto...")
        while self.running:
            try:
                # Recebe o tópico, ID do remetente e dados de texto
                topic, sender_id, text_data = self.text_sub_socket.recv_multipart()
                
                # Exibe a mensagem se não for a própria mensagem enviada
                if sender_id.decode('utf-8') != self.client_id:
                    print(f"--> {text_data.decode('utf-8')}")
            except zmq.Again:
                pass  # No messages yet
            except Exception as e:
                print(f"Erro ao receber texto: {e}")
                break

    def start(self):
        """Inicia todos os threads de comunicação."""
        # Threads de envio
        threading.Thread(target=self._send_audio, daemon=True).start()
        threading.Thread(target=self._send_video, daemon=True).start()
        threading.Thread(target=self._send_text, daemon=True).start()

        # Threads de recebimento
        threading.Thread(target=self._receive_audio, daemon=True).start()
        threading.Thread(target=self._receive_video, daemon=True).start()
        threading.Thread(target=self._receive_text, daemon=True).start()

        # Mantém o programa principal rodando para que os threads continuem
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nCliente encerrado.")
        finally:
            self.stop()

    def stop(self):
        """Encerra todos os recursos."""
        self.running = False
        print("Encerrando sockets e streams...")
        time.sleep(2) # Pequena pausa para os threads terminarem limpo
        self.audio_pub_socket.close()
        self.audio_sub_socket.close()
        self.video_pub_socket.close()
        self.video_sub_socket.close()
        self.text_pub_socket.close()
        self.text_sub_socket.close()
        self.context.term()
        if self.pyaudio_instance:
            self.pyaudio_instance.terminate()
        cv2.destroyAllWindows()
        print("Cliente encerrado com sucesso.")
        sys.exit(0) # Sai do programa

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python client.py <seu_ID_de_cliente>")
        sys.exit(1)
    
    client_id = sys.argv[1]
    client = VideoConferenceClient(client_id)
    client.start()