# Endereços e portas para o broker
BROKER_IP = "127.0.0.1"

# Portas para o forwarder de Áudio
AUDIO_XSUB_PORT = 6000
AUDIO_XPUB_PORT = 6001

# Portas para o forwarder de Vídeo
VIDEO_XSUB_PORT = 6002 # Era 6001, agora é 6002 para não colidir
VIDEO_XPUB_PORT = 6003

# Portas para o forwarder de Texto
TEXT_XSUB_PORT = 6004 # Era 6002, agora é 6004 para não colidir
TEXT_XPUB_PORT = 6005

# Tamanhos de buffer e frames
AUDIO_CHUNK_SIZE = 1024
VIDEO_FRAME_WIDTH = 640
VIDEO_FRAME_HEIGHT = 480
FPS = 30

# Tópicos para o modelo PUB/SUB
TOPIC_AUDIO = b"AUDIO"
TOPIC_VIDEO = b"VIDEO"
TOPIC_TEXT = b"TEXT"

# Identificador do cliente (para evitar eco de mensagens)
CLIENT_ID = b"UNKNOWN"