// Listen for messages from the popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'getEmailContent') {
        try {
            const emailData = extractEmailContent();
            console.log('Extracted email data:', emailData); // Debug log
            sendResponse(emailData);
        } catch (error) {
            console.error('Error extracting email:', error);
            sendResponse({ error: error.message });
        }
    }
    return true;
});

// Function to extract email content from Gmail
function extractEmailContent() {
    console.log('Starting email extraction...'); // Debug log

    // Get the email subject
    const subject = document.querySelector('h2.hP')?.textContent || 
                   document.querySelector('div[data-thread-title]')?.textContent || 
                   '';

    // Get the sender
    const sender = document.querySelector('span.gD')?.getAttribute('email') || 
                  document.querySelector('span[email]')?.getAttribute('email') || 
                  '';

    // Get the email body
    const bodyElement = document.querySelector('div.a3s.aiL') || 
                       document.querySelector('div[role="main"] div[dir="ltr"]') ||
                       document.querySelector('div[role="main"]');
    
    const body = bodyElement ? bodyElement.textContent.trim() : '';

    console.log('Found elements:', { // Debug log
        subject: !!subject,
        sender: !!sender,
        body: !!body
    });

    // If we're in the inbox view, try to get the preview
    if (!body && document.querySelector('.bog')) {
        const preview = document.querySelector('.bog').textContent.trim();
        return {
            subject: subject || 'No subject',
            sender: sender || 'Unknown sender',
            body: preview || 'No content available'
        };
    }

    // Validate that we have at least some content
    if (!subject && !body) {
        throw new Error('Could not find email content. Please make sure you are viewing an email.');
    }

    return {
        subject: subject || 'No subject',
        sender: sender || 'Unknown sender',
        body: body || 'No content available'
    };
}

// Only set up the observer if it hasn't been set up before
if (!window.emailReaderObserver) {
    window.emailReaderObserver = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.addedNodes.length) {
                console.log('Gmail content updated'); // Debug log
            }
        });
    });

    // Start observing the document with the configured parameters
    window.emailReaderObserver.observe(document.body, {
        childList: true,
        subtree: true
    });
} 