function logURL(requestDetails) {
  let url = requestDetails.url;
//   console.log(`bobrNet detected: ${url}`);
  send(url);
}

browser.webRequest.onBeforeRequest.addListener(logURL, {
  urls: ["<all_urls>"],
});

function send(url, host = "127.0.0.1", port = 24096) {
    if (url == "ws://127.0.0.1:24096/" || url.startsWith("http://10.7.12.130:8081/socket.io/")) {
        // console.log("Ignoring " + url)
        return
    }
  const socket = new WebSocket(`ws://${host}:${port}`);
// console.log("Sending to socket " + url)

  socket.addEventListener("open", (event) => {
    try {
      if (url) {
        socket.send(encodeURI(url));
      }
    } catch (error) {
      console.log("Error: opening web socket failed. " + error);
    }
  });
}
