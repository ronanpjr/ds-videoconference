import zmq

def create_pub_socket(context, port):
    """Cria um socket PUB para publicação."""
    socket = context.socket(zmq.PUB)
    socket.bind(f"tcp://*:{port}")
    return socket

def create_sub_socket(context, ip, port, topic=b""):
    """Cria um socket SUB para assinatura."""
    socket = context.socket(zmq.SUB)
    socket.connect(f"tcp://{ip}:{port}")
    socket.setsockopt_string(zmq.SUBSCRIBE, topic.decode('utf-8'))
    return socket
