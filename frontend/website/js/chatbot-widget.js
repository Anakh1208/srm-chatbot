// Chatbot Widget Logic
const API_URL = 'http://127.0.0.1:8001/chat';

// Elements
const toggleBtn = document.getElementById('chatbot-toggle');
const closeBtn = document.getElementById('chatbot-close');
const chatWindow = document.getElementById('chatbot-window');
const chatMessages = document.getElementById('chat-messages');
const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');
const quickBtns = document.querySelectorAll('.quick-btn');

// Toggle chatbot
toggleBtn.addEventListener('click', () => {
    chatWindow.classList.toggle('hidden');
});

closeBtn.addEventListener('click', () => {
    chatWindow.classList.add('hidden');
});

// Quick action buttons
quickBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        const query = btn.dataset.query;
        sendMessage(query);
    });
});

// Send message on Enter
chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

// Send button
sendBtn.addEventListener('click', () => {
    sendMessage();
});

// Send message function
async function sendMessage(predefinedQuery = null) {
    const query = predefinedQuery || chatInput.value.trim();
    
    if (!query) return;
    
    // Add user message
    addMessage(query, 'user');
    
    // Clear input
    chatInput.value = '';
    
    // Show typing indicator
    showTypingIndicator();
    
    try {
        // Call API
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query })
        });
        
        const data = await response.json();
        
        // Remove typing indicator
        removeTypingIndicator();
        
        // Add bot response
        addMessage(data.answer, 'bot');
        
    } catch (error) {
        console.error('Error:', error);
        removeTypingIndicator();
        addMessage('Sorry, I encountered an error. Please try again.', 'bot');
    }
}

// Add message to chat
function addMessage(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = sender === 'bot' ? 'bot-message' : 'user-message';
    
    if (sender === 'bot') {
        messageDiv.innerHTML = `
            <img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 40 40'%3E%3Ccircle cx='20' cy='20' r='18' fill='%230066cc'/%3E%3Ctext x='50%25' y='55%25' text-anchor='middle' font-size='20' fill='white'%3EP%3C/text%3E%3C/svg%3E" alt="Bot" class="msg-avatar">
            <div class="message-content">
                <p>${formatMessage(text)}</p>
            </div>
        `;
    } else {
        messageDiv.innerHTML = `
            <div class="message-content">
                <p>${text}</p>
            </div>
        `;
    }
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Format message (preserve line breaks)
function formatMessage(text) {
    return text.replace(/\n/g, '<br>');
}

// Show typing indicator
function showTypingIndicator() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'bot-message typing-message';
    typingDiv.id = 'typing-indicator';
    typingDiv.innerHTML = `
        <img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 40 40'%3E%3Ccircle cx='20' cy='20' r='18' fill='%230066cc'/%3E%3Ctext x='50%25' y='55%25' text-anchor='middle' font-size='20' fill='white'%3EP%3C/text%3E%3C/svg%3E" alt="Bot" class="msg-avatar">
        <div class="message-content typing-indicator">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>
    `;
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Remove typing indicator
function removeTypingIndicator() {
    const typing = document.getElementById('typing-indicator');
    if (typing) typing.remove();
}

// Auto-open chatbot after 3 seconds (optional)
setTimeout(() => {
    chatWindow.classList.remove('hidden');
}, 3000);