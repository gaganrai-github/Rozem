const video = document.getElementById("remoteVideo");
let socket = io();
let peerConnection = new RTCPeerConnection();

socket.on("offer", async (offer) => {
    await peerConnection.setRemoteDescription(new RTCSessionDescription(offer));
    let answer = await peerConnection.createAnswer();
    await peerConnection.setLocalDescription(answer);
    socket.emit("answer", answer);
});

peerConnection.ontrack = (event) => {
    video.srcObject = event.streams[0];
};
