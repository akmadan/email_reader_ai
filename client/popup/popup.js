document.addEventListener('DOMContentLoaded', function() {
    const summarizeBtn = document.getElementById('summarizeBtn');
    const statusContainer = document.querySelector('.status-container');
    const statusText = document.querySelector('.status-text');
    const summaryContainer = document.querySelector('.summary-container');
    const summaryText = document.getElementById('summaryText');
    const audioPlayer = document.getElementById('audioPlayer');

    // Function to update status
    function updateStatus(text, isError = false) {
        statusText.textContent = text;
        statusContainer.classList.toggle('error', isError);
    }

    // Function to show loading state
    function setLoading(isLoading) {
        statusContainer.classList.toggle('loading', isLoading);
        summarizeBtn.disabled = isLoading;
    }

    // Function to show summary
    function showSummary(summary, audioUrl) {
        summaryText.textContent = summary;
        audioPlayer.src = audioUrl;
        summaryContainer.classList.remove('hidden');
    }

    // Function to check if server is running
    async function checkServerStatus() {
        try {
            const response = await fetch('http://localhost:8000/health');
            return response.ok;
        } catch (error) {
            return false;
        }
    }

    // Function to inject content script if not already present
    async function ensureContentScript(tabId) {
        try {
            await chrome.scripting.executeScript({
                target: { tabId: tabId },
                files: ['content/content.js']
            });
        } catch (error) {
            console.log('Content script already injected or injection failed:', error);
        }
    }

    // Function to get current email content
    async function getCurrentEmail() {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        
        if (!tab.url.includes('mail.google.com')) {
            throw new Error('Please open Gmail to use this extension');
        }

        try {
            // Ensure content script is injected
            await ensureContentScript(tab.id);
            
            // Wait a bit for the script to initialize
            await new Promise(resolve => setTimeout(resolve, 500));
            
            const response = await chrome.tabs.sendMessage(tab.id, { action: 'getEmailContent' });
            
            if (response.error) {
                throw new Error(response.error);
            }
            
            return response;
        } catch (error) {
            console.error('Error getting email content:', error);
            if (error.message.includes('Receiving end does not exist')) {
                throw new Error('Please refresh the Gmail page and try again');
            }
            throw error;
        }
    }

    // Function to summarize email
    async function summarizeEmail(emailData) {
        try {
            // Check if server is running first
            const isServerRunning = await checkServerStatus();
            if (!isServerRunning) {
                throw new Error('Server is not running. Please start the FastAPI server.');
            }

            const response = await fetch('http://localhost:8000/api/v1/summarize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(emailData)
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || 'Failed to summarize email');
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error summarizing email:', error);
            if (error.message.includes('Failed to fetch')) {
                throw new Error('Could not connect to server. Please make sure the FastAPI server is running.');
            }
            throw error;
        }
    }

    // Event listener for summarize button
    summarizeBtn.addEventListener('click', async () => {
        try {
            setLoading(true);
            updateStatus('Getting email content...');

            const emailData = await getCurrentEmail();
            updateStatus('Generating summary...');

            const result = await summarizeEmail(emailData);
            showSummary(result.summary, result.summary_audio_link);
            
            updateStatus('Ready');
        } catch (error) {
            updateStatus(error.message, true);
        } finally {
            setLoading(false);
        }
    });
}); 