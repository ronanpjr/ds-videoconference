# 📹 DS Videoconference

**DS Videoconference** is a distributed video conferencing system built with Python, focused on real-time video streaming over network sockets. The project explores distributed systems concepts, image processing, and networking protocols to achieve low-latency communication between multiple clients.

## ✨ Features

* **Real-Time Video Streaming**: High-quality video capture and transmission using OpenCV.
* **Client-Server Architecture**: Robust communication using TCP/UDP Sockets for frame exchange.
* **Data Optimization**: Efficient frame encoding and compression to minimize bandwidth usage.
* **Multi-Client Support**: Handles simultaneous connections from multiple users.

## 🛠️ Tech Stack

* **Python**: Core programming language.
* **OpenCV**: Computer vision library for video stream manipulation.
* **Sockets**: Network programming interface for node-to-node communication.
* **Pickle/Struct**: Data serialization for packet transmission.

## 🚀 Getting Started

### Prerequisites

* Python 3.8 or higher installed.
* A functional webcam (for the client side).

### Installation

1. Clone the repository:
```bash
git clone https://github.com/ronanpjr/ds-videoconference.git
cd ds-videoconference

```


2. Install dependencies:
```bash
pip install opencv-python numpy

```



### Running the Application

1. **Start the Server**:
```bash
python server.py

```


2. **Start the Client**:
On another terminal (or another machine on the same network, adjusting the server IP):
```bash
python client.py

```



## 🏗️ System Architecture

The project implements a distributed model where the server acts as a central hub, managing and relaying encoded video packets sent by clients. The networking logic prioritizes frame fluidity, employing buffering techniques to mitigate jitter and network instability.

## 🤝 Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create.

1. **Fork** the project.
2. Create your **Feature Branch** (`git checkout -b feature/AmazingFeature`).
3. **Commit** your changes (`git commit -m 'Add some AmazingFeature'`).
4. **Push** to the branch (`git push origin feature/AmazingFeature`).
5. Open a **Pull Request**.

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

Developed by [Ronan Pereira](https://github.com/ronanpjr) 💻
