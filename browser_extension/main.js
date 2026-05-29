function logURL(requestDetails) {
  console.log(`bobrNet detected: ${requestDetails.url}`);
}

browser.webRequest.onBeforeRequest.addListener(logURL, {
  urls: ["<all_urls>"],
});