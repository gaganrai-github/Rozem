const startButton = document.getElementById("start");
const stopButton = document.getElementById("stop");
const video = document.getElementById("screenVideo");
let peerConnection;
let socket = io();

startButton.onclick = async () => {
    try {
        const stream = await navigator.mediaDevices.getDisplayMedia({ video: true });

        video.srcObject = stream;

        peerConnection = new RTCPeerConnection();
        stream.getTracks().forEach(track => peerConnection.addTrack(track, stream));

        const offer = await peerConnection.createOffer();
        await peerConnection.setLocalDescription(offer);

        socket.emit("offer", offer);

        startButton.disabled = true;
        stopButton.disabled = false;

        stopButton.onclick = () => {
            stream.getTracks().forEach(track => track.stop());
            peerConnection.close();
            startButton.disabled = false;
            stopButton.disabled = true;
        };

    } catch (error) {
        console.error("Error starting screen share:", error);
    }
};

socket.on("answer", async (answer) => {
    await peerConnection.setRemoteDescription(new RTCSessionDescription(answer));
});
