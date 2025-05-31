// Background script for Email Reader AI extension
chrome.runtime.onInstalled.addListener(() => {
    console.log('Email Reader AI extension installed');
});

// Listen for messages from content script or popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'checkServerStatus') {
        // Check if the server is running
        fetch('http://localhost:8000/health')
            .then(response => response.json())
            .then(data => {
                sendResponse({ status: 'ok', data });
            })
            .catch(error => {
                sendResponse({ status: 'error', message: 'Server not available' });
            });
        return true; // Required for async sendResponse
    }
}); 