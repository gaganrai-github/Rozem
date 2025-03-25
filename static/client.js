const startButton = document.getElementById("start");
const stopButton = document.getElementById("stop");
const video = document.getElementById("screenVideo");
let socket = io();
let peerConnection;
let screenStream;

startButton.onclick = async () => {
    try {
        // Laptop ka Screen Capture Karo
        screenStream = await navigator.mediaDevices.getDisplayMedia({
            video: { cursor: "always" }, 
            audio: false
        });

        // Video Tag me Dikhana
        video.srcObject = screenStream;

        // WebRTC Connection
        peerConnection = new RTCPeerConnection();
        screenStream.getTracks().forEach(track => peerConnection.addTrack(track, screenStream));

        // Create & Send Offer
        let offer = await peerConnection.createOffer();
        await peerConnection.setLocalDescription(offer);
        socket.emit("offer", offer);

        startButton.disabled = true;
        stopButton.disabled = false;

        stopButton.onclick = () => {
            screenStream.getTracks().forEach(track => track.stop());
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
