// Initialize markdown converter
const converter = new showdown.Converter();

// Chat windows
const basicChat = document.getElementById('basic-chat');
const ragChat = document.getElementById('rag-chat');
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');

// Configuration
const config = {
    basicEndpoint: 'https://neotitan.ddns.net:9214/v1/chat/completions',
    ragEndpoint: 'https://neotitan.ddns.net:9215/v1/chat/completions',
    headers: {
        "Content-Type": "application/json"
    }
};

const healthChecks = {
    basicEndpoint: 'https://neotitan.ddns.net:9214/v1/health',
    ragEndpoint: 'https://neotitan.ddns.net:9215/health'
};

// Initialize conversation histories
const basicHistory = [
    { role: "system", content: "You are a helpful AI assistant." }
];

const ragHistory = [
    { role: "system", content: "You are a helpful AI assistant with access to additional information via a vector database." }
];

// Logging helper
function logInfo(message, type = 'info') {
    const styles = {
        info: 'color: #2563eb; font-weight: bold;',
        success: 'color: #059669; font-weight: bold;',
        warning: 'color: #d97706; font-weight: bold;',
        error: 'color: #dc2626; font-weight: bold;'
    };
    console.log(`%c${message}`, styles[type]);
}

// Helper function to create message elements
function createMessageElement(message, isUser) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
    
    const iconSpan = document.createElement('span');
    iconSpan.className = 'message-icon';
    iconSpan.innerHTML = isUser ? '👤' : '🤖';
    
    const contentSpan = document.createElement('span');
    contentSpan.className = 'message-content';
    contentSpan.innerHTML = converter.makeHtml(message);
    
    messageDiv.appendChild(iconSpan);
    messageDiv.appendChild(contentSpan);
    
    return messageDiv;
}

// Helper function to scroll chat to bottom
function scrollToBottom(element) {
    element.scrollTop = element.scrollHeight;
}

// Function to handle basic model response
async function getBasicResponse(message) {
    try {
        // Add user message to history
        basicHistory.push({ role: "user", content: message });

        logInfo('🚀 Sending request to basic Phi-4 model...', 'info');
        const response = await fetch(config.basicEndpoint, {
            method: 'POST',
            headers: config.headers,
            body: JSON.stringify({
                model: "phi-4",
                messages: basicHistory,
                temperature: 0.7,
                max_tokens: -1,
                stream: true
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        logInfo('📡 Receiving streamed response from basic model...', 'info');
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let text = '';

        let botMessage = createMessageElement('', false);
        basicChat.appendChild(botMessage);
        const contentSpan = botMessage.querySelector('.message-content');

        while (true) {
            const {done, value} = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value);
            const lines = chunk.split('\n').filter(line => line.trim());

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = line.slice(6);
                    if (data === '[DONE]') {
                        // Add assistant's complete response to history
                        basicHistory.push({ role: "assistant", content: text });
                        logInfo('✅ Basic model response complete', 'success');
                        break;
                    }

                    try {
                        const parsed = JSON.parse(data);
                        const content = parsed.choices[0]?.delta?.content || '';
                        if (content) {
                            text += content;
                            contentSpan.innerHTML = converter.makeHtml(text);
                            scrollToBottom(basicChat);
                        }
                    } catch (e) {
                        console.error('Error parsing chunk:', e);
                    }
                }
            }
        }
    } catch (error) {
        logInfo(`❌ Basic model error: ${error.message}`, 'error');
        const errorMessage = createMessageElement(`Error: ${error.message}`, false);
        basicChat.appendChild(errorMessage);
    }
}

// Function to handle RAG model response
async function getRagResponse(message) {
    try {
        // Add user message to history
        ragHistory.push({ role: "user", content: message });

        logInfo('🔍 Initiating RAG-enhanced response...', 'info');
        
        // Create message element with loading indicator
        let botMessage = createMessageElement('', false);
        const loadingIndicator = document.createElement('div');
        loadingIndicator.className = 'typing-indicator';
        loadingIndicator.innerHTML = `
            Generating RAG-enhanced response
            <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        `;
        botMessage.querySelector('.message-content').appendChild(loadingIndicator);
        ragChat.appendChild(botMessage);
        scrollToBottom(ragChat);

        const response = await fetch(config.ragEndpoint, {
            method: 'POST',
            headers: config.headers,
            body: JSON.stringify({
                model: "phi-4",
                messages: ragHistory,
                temperature: 0.7,
                max_tokens: -1,
                stream: true
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        logInfo('📡 Receiving RAG-enhanced response stream...', 'info');
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let text = '';
        let displayBuffer = '';
        let lastDisplayTime = 0;
        const DISPLAY_INTERVAL = 8;

        const contentSpan = botMessage.querySelector('.message-content');

        const updateDisplay = () => {
            const now = performance.now();
            if (now - lastDisplayTime >= DISPLAY_INTERVAL && displayBuffer !== text) {
                contentSpan.innerHTML = converter.makeHtml(text);
                scrollToBottom(ragChat);
                displayBuffer = text;
                lastDisplayTime = now;
            }
        };

        while (true) {
            const {done, value} = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value);
            const lines = chunk.split('\n').filter(line => line.trim());

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = line.slice(6).trim();
                    if (!data) continue;

                    if (data === '[DONE]') {
                        // Add assistant's complete response to history
                        ragHistory.push({ role: "assistant", content: text });
                        contentSpan.innerHTML = converter.makeHtml(text);
                        scrollToBottom(ragChat);
                        logInfo('✅ RAG-enhanced response complete', 'success');
                        break;
                    }

                    try {
                        const parsed = JSON.parse(data);
                        const content = parsed.choices?.[0]?.delta?.content || '';
                        if (content) {
                            text += content;
                            requestAnimationFrame(updateDisplay);
                        }
                    } catch (e) {
                        if (data && !data.includes('data: data:')) {
                            console.debug('Skipping incomplete chunk');
                        }
                    }
                }
            }
        }
    } catch (error) {
        logInfo(`❌ RAG model error: ${error.message}`, 'error');
        const errorMessage = createMessageElement(`Error: ${error.message}`, false);
        ragChat.appendChild(errorMessage);
    }
}

// Function to handle form submission
chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const message = userInput.value.trim();
    if (!message) return;
    
    logInfo('🎯 Processing new user query...', 'info');
    
    // Clear input
    userInput.value = '';
    
    // Add user message to both chats
    const userMessageBasic = createMessageElement(message, true);
    const userMessageRag = createMessageElement(message, true);
    basicChat.appendChild(userMessageBasic);
    ragChat.appendChild(userMessageRag);
    
    // Scroll both chats to bottom
    scrollToBottom(basicChat);
    scrollToBottom(ragChat);
    
    // Get responses sequentially
    await getBasicResponse(message);
    await getRagResponse(message);
    
    logInfo('👍 Query processing complete!', 'success');
});
