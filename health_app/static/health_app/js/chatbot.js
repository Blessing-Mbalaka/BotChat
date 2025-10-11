class HealthBotChat {
    constructor() {
        this.chatContainer = document.getElementById('chatContainer');
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.chatForm = document.getElementById('chatForm');
        this.typingIndicator = document.getElementById('typingIndicator');
        this.clearChatBtn = document.getElementById('clearChat');
        this.exportChatBtn = document.getElementById('exportChat');
        
        this.messages = [];
        this.isTyping = false;
        
        // Text-to-Speech configuration
        this.speechEnabled = true;
        this.speechSynthesis = window.speechSynthesis;
        this.currentVoice = null;
        this.speechRate = 0.9;
        this.speechPitch = 1.0;
        this.speechVolume = 0.8;
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.loadChatHistory();
        this.setupQuickActions();
        this.setupSuggestionChips();
        this.initializeSpeech();
    }
    
    bindEvents() {
        // Form submission
        this.chatForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.sendMessage();
        });
        
        // Enter key handling
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Clear chat
        this.clearChatBtn.addEventListener('click', () => {
            this.clearChat();
        });
        
        // Export chat
        this.exportChatBtn.addEventListener('click', () => {
            this.exportChat();
        });

        // Speech toggle
        const speechToggle = document.getElementById('speechToggle');
        if (speechToggle) {
            speechToggle.addEventListener('click', () => {
                this.toggleSpeech();
            });
        }

        // Test voice button
        const testVoiceBtn = document.getElementById('testVoiceBtn');
        if (testVoiceBtn) {
            testVoiceBtn.addEventListener('click', () => {
                this.testSpeech();
            });
        }
        
        // Auto-resize input
        this.messageInput.addEventListener('input', () => {
            this.autoResizeInput();
        });
    }
    
    setupQuickActions() {
        const actionButtons = document.querySelectorAll('.action-btn');
        actionButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                const action = btn.dataset.action;
                this.handleQuickAction(action);
            });
        });
    }
    
    setupSuggestionChips() {
        const suggestionChips = document.querySelectorAll('.suggestion-chip');
        suggestionChips.forEach(chip => {
            chip.addEventListener('click', () => {
                const suggestion = chip.dataset.suggestion;
                this.messageInput.value = suggestion;
                this.sendMessage();
            });
        });
    }

    initializeSpeech() {
        if (!this.speechSynthesis) {
            console.log('🔇 Speech synthesis not supported');
            this.speechEnabled = false;
            return;
        }

        // Load speech preference from localStorage
        const savedPreference = localStorage.getItem('healthbot_speech_enabled');
        if (savedPreference !== null) {
            this.speechEnabled = savedPreference === 'true';
        }

        // Wait for voices to be loaded
        const loadVoices = () => {
            const voices = this.speechSynthesis.getVoices();
            
            console.log('🎤 Available voices:', voices.map(v => ({ name: v.name, lang: v.lang, gender: v.gender || 'unknown' })));
            
            // Find the best female voice
            const femaleVoices = voices.filter(voice => 
                voice.name.toLowerCase().includes('female') ||
                voice.name.toLowerCase().includes('woman') ||
                voice.name.toLowerCase().includes('zira') ||
                voice.name.toLowerCase().includes('susan') ||
                voice.name.toLowerCase().includes('samantha') ||
                voice.name.toLowerCase().includes('karen') ||
                voice.name.toLowerCase().includes('hazel') ||
                voice.name.toLowerCase().includes('anna') ||
                voice.name.toLowerCase().includes('catherine') ||
                voice.name.toLowerCase().includes('eva') ||
                voice.name.toLowerCase().includes('aria') ||
                (voice.lang.startsWith('en') && voice.gender === 'female')
            );
            
            console.log('🎤 Female voices found:', femaleVoices.map(v => v.name));

            // Select the best female voice
            if (femaleVoices.length > 0) {
                this.currentVoice = femaleVoices[0];
                console.log('🎤 Selected female voice:', this.currentVoice.name);
            } else {
                // Fallback: find any English voice and check if it sounds female
                const englishVoices = voices.filter(voice => 
                    voice.lang.startsWith('en') || voice.name.toLowerCase().includes('english')
                );
                
                console.log('🎤 English voices found:', englishVoices.map(v => v.name));
                
                if (englishVoices.length > 0) {
                    // Try to pick one that might be female based on common patterns
                    this.currentVoice = englishVoices.find(voice => 
                        !voice.name.toLowerCase().includes('male') &&
                        !voice.name.toLowerCase().includes('david') &&
                        !voice.name.toLowerCase().includes('mark') &&
                        !voice.name.toLowerCase().includes('alex') &&
                        !voice.name.toLowerCase().includes('daniel')
                    ) || englishVoices[0];
                    console.log('🎤 Selected fallback voice:', this.currentVoice.name);
                } else if (voices.length > 0) {
                    // Last resort: use any available voice
                    this.currentVoice = voices[0];
                    console.log('🎤 Selected last resort voice:', this.currentVoice.name);
                }
            }

            if (this.currentVoice) {
                console.log('✅ Speech initialized with voice:', this.currentVoice.name);
            } else {
                console.log('⚠️ No suitable voice found');
            }

            // Update UI elements after voice is loaded
            this.updateSpeechToggleButton();
            this.updateSpeechStatus(false);
        };

        // Load voices
        if (this.speechSynthesis.getVoices().length > 0) {
            loadVoices();
        } else {
            this.speechSynthesis.onvoiceschanged = loadVoices;
        }
    }
    
    handleQuickAction(action) {
        const actionMessages = {
            'symptoms': 'I\'d like to check some symptoms I\'m experiencing.',
            'research': 'Show me medical research articles and studies with links.',
            'sa-doctors': 'Find doctors and medical specialists in South Africa.',
            'medications': 'Can you help me with information about medications?',
            'wellness': 'I\'m looking for wellness and health tips.',
            'emergency': 'I need information about emergency medical situations.'
        };
        
        if (actionMessages[action]) {
            this.messageInput.value = actionMessages[action];
            this.sendMessage();
        }
    }
    
    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message || this.isTyping) return;
        
        // Clear welcome message if it exists
        const welcomeMessage = document.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.style.display = 'none';
        }
        
        // Add user message to chat
        this.addMessage(message, 'user');
        this.messageInput.value = '';
        this.autoResizeInput();
        
        // Show typing indicator
        this.showTypingIndicator();
        
        try {
            // Send message to backend
            const response = await fetch('/chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken(),
                },
                body: JSON.stringify({
                    message: message,
                    conversation_id: this.getConversationId()
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            // Hide typing indicator
            this.hideTypingIndicator();
            
            if (data.success) {
                // Add bot response with typing effect
                this.addMessage(data.response, 'bot', true);
                
                // Update status indicator
                this.updateStatusIndicator(data.ai_powered);
                
                // Update conversation ID if provided
                if (data.conversation_id) {
                    this.setConversationId(data.conversation_id);
                }
                
                // Speak the response after typing animation
                setTimeout(() => {
                    console.log('⏰ Timeout triggered for speech');
                    this.speakMessage(data.response);
                }, 2000); // Wait for typing animation to finish
                
            } else {
                this.addErrorMessage(data.error || 'Sorry, I encountered an error. Please try again.');
            }
            
        } catch (error) {
            console.error('Error sending message:', error);
            this.hideTypingIndicator();
            this.addErrorMessage('I\'m having trouble connecting right now. Please check your connection and try again.');
        }
        
        // Scroll to bottom
        this.scrollToBottom();
    }
    
    addMessage(content, sender, typeEffect = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'message-avatar';
        avatarDiv.innerHTML = sender === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        if (typeEffect && sender === 'bot') {
            this.typeMessage(contentDiv, content);
        } else {
            contentDiv.innerHTML = this.formatMessage(content);
        }
        
        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(contentDiv);
        
        this.chatContainer.appendChild(messageDiv);
        
        // Store message in history
        this.messages.push({ content, sender, timestamp: new Date() });
        this.saveChatHistory();
        
        this.scrollToBottom();
    }
    
    typeMessage(element, text, speed = 30) {
        element.innerHTML = '';
        let i = 0;
        
        const typeInterval = setInterval(() => {
            if (i < text.length) {
                element.innerHTML += text.charAt(i);
                i++;
                this.scrollToBottom();
            } else {
                clearInterval(typeInterval);
                element.innerHTML = this.formatMessage(text);
            }
        }, speed);
    }
    
    formatMessage(message) {
        // Debug: Log the original message
        console.log('🔍 Original message:', message);
        
        // Convert line breaks to <br> tags
        message = message.replace(/\n/g, '<br>');
        
        // Format bold text (but avoid interfering with existing HTML)
        message = message.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Format italic text (but avoid interfering with existing HTML)
        message = message.replace(/\*(.*?)\*/g, '<em>$1</em>');
        
        // Format markdown-style links [text](url) - only if not already HTML
        message = message.replace(/\[([^\[\]]+)\]\(([^()]+)\)/g, function(match, text, url) {
            console.log('🔗 Found markdown link:', text, '->', url);
            return `<a href="${url}" target="_blank" rel="noopener noreferrer" class="medical-link">${text} <i class="fas fa-external-link-alt" style="font-size: 0.8em; opacity: 0.7;"></i></a>`;
        });
        
        // Add styling class to existing HTML links
        message = message.replace(/<a href="([^"]+)"([^>]*)>([^<]+)<\/a>/g, function(match, url, attributes, text) {
            console.log('🔗 Found HTML link:', text, '->', url);
            // Add our styling class if not already present
            if (!attributes.includes('class=')) {
                attributes += ' class="medical-link"';
            } else if (!attributes.includes('medical-link')) {
                attributes = attributes.replace(/class="([^"]*)"/, 'class="$1 medical-link"');
            }
            // Add external link icon
            return `<a href="${url}"${attributes}>${text} <i class="fas fa-external-link-alt" style="font-size: 0.8em; opacity: 0.7;"></i></a>`;
        });
        
        // Format regular URLs (fallback) - avoid double-linking
        message = message.replace(/(?<!href=["'])(https?:\/\/[^\s<"']+)(?![^<]*<\/a>)/g, function(match, url) {
            console.log('🌐 Found plain URL:', url);
            return `<a href="${url}" target="_blank" rel="noopener noreferrer" class="medical-link">${url}</a>`;
        });
        
        // Format section headers with emojis
        message = message.replace(/(🏥|🏨|🚑|📚|🏛️|💡|⚠️) \*\*(.*?)\*\*/g, '<div class="section-header">$1 <strong>$2</strong></div>');
        
        // Format bullet points with better styling
        message = message.replace(/• (.*?)(<br>|$)/g, '<div class="bullet-point">• $1</div>');
        
        // Debug: Log the formatted message
        console.log('✅ Formatted message:', message);
        
        return message;
    }

    speakMessage(message) {
        console.log('🎤 speakMessage called with enabled:', this.speechEnabled);
        console.log('🎤 speechSynthesis available:', !!this.speechSynthesis);
        console.log('🎤 currentVoice:', this.currentVoice?.name);
        
        if (!this.speechEnabled) {
            console.log('🔇 Speech disabled by user');
            return;
        }
        
        if (!this.speechSynthesis) {
            console.log('🔇 Speech synthesis not available');
            return;
        }
        
        if (!this.currentVoice) {
            console.log('🔇 No voice selected, attempting to reload voices');
            this.initializeSpeech();
            return;
        }

        // Stop any currently speaking utterance
        this.speechSynthesis.cancel();

        // Clean the message for speech (remove HTML tags and format for speaking)
        let cleanMessage = this.cleanMessageForSpeech(message);
        console.log('🗣️ Clean message for speech:', cleanMessage);
        
        // Don't speak if message is too long (over 500 characters)
        if (cleanMessage.length > 500) {
            console.log('🔇 Message too long for speech:', cleanMessage.length, 'characters');
            cleanMessage = cleanMessage.substring(0, 500) + '...';
        }

        const utterance = new SpeechSynthesisUtterance(cleanMessage);
        
        // Configure the voice
        utterance.voice = this.currentVoice;
        utterance.rate = this.speechRate;
        utterance.pitch = this.speechPitch;
        utterance.volume = this.speechVolume;

        console.log('🎵 Utterance configured:', {
            voice: utterance.voice?.name,
            rate: utterance.rate,
            pitch: utterance.pitch,
            volume: utterance.volume,
            text: cleanMessage.substring(0, 50) + '...'
        });

        // Add event listeners
        utterance.onstart = () => {
            console.log('🎤 Speech started successfully');
            this.updateSpeechStatus(true);
        };

        utterance.onend = () => {
            console.log('🔇 Speech finished');
            this.updateSpeechStatus(false);
        };

        utterance.onerror = (event) => {
            console.error('❌ Speech error:', event.error, event);
            this.updateSpeechStatus(false);
        };

        // Test if speech synthesis is working
        if (this.speechSynthesis.paused) {
            this.speechSynthesis.resume();
        }

        console.log('🚀 Attempting to speak...');
        
        // Speak the message
        try {
            this.speechSynthesis.speak(utterance);
            console.log('✅ Speech synthesis.speak() called successfully');
        } catch (error) {
            console.error('❌ Error calling speak():', error);
        }
    }

    cleanMessageForSpeech(message) {
        // Remove HTML tags
        let cleaned = message.replace(/<[^>]*>/g, ' ');
        
        // Replace multiple spaces with single space
        cleaned = cleaned.replace(/\s+/g, ' ');
        
        // Remove markdown formatting
        cleaned = cleaned.replace(/\*\*(.*?)\*\*/g, '$1'); // Bold
        cleaned = cleaned.replace(/\*(.*?)\*/g, '$1'); // Italic
        cleaned = cleaned.replace(/\[([^\]]+)\]\([^)]+\)/g, '$1'); // Links
        
        // Replace bullet points with "Point:"
        cleaned = cleaned.replace(/•/g, 'Point:');
        
        // Replace emojis with words for better pronunciation
        const emojiReplacements = {
            '🏥': 'Medical centers',
            '🏨': 'Hospitals',
            '🚑': 'Emergency services',
            '📚': 'Medical articles',
            '🏛️': 'Health organizations',
            '💡': 'Tip',
            '⚠️': 'Important',
            '❤️': 'Heart',
            '🧠': 'Brain',
            '🇿🇦': 'South African'
        };
        
        for (const [emoji, replacement] of Object.entries(emojiReplacements)) {
            cleaned = cleaned.replace(new RegExp(emoji, 'g'), replacement);
        }
        
        // Clean up punctuation for better speech flow
        cleaned = cleaned.replace(/---/g, '. '); // Replace dividers with pauses
        cleaned = cleaned.replace(/\.\.\./g, '...'); // Keep ellipsis
        
        return cleaned.trim();
    }

    updateSpeechStatus(isSpeaking) {
        const statusElement = document.getElementById('speechStatus');
        if (statusElement) {
            if (isSpeaking) {
                statusElement.innerHTML = '<i class="fas fa-volume-up pulse"></i> Speaking';
                statusElement.className = 'text-info';
            } else {
                statusElement.innerHTML = '<i class="fas fa-volume-up"></i> Ready';
                statusElement.className = 'text-muted';
            }
        }
    }

    toggleSpeech() {
        this.speechEnabled = !this.speechEnabled;
        
        if (!this.speechEnabled) {
            this.speechSynthesis.cancel(); // Stop current speech
        } else {
            // Test speech when enabled
            this.testSpeech();
        }
        
        this.updateSpeechToggleButton();
        
        // Save preference
        localStorage.setItem('healthbot_speech_enabled', this.speechEnabled);
        
        console.log('🔊 Speech', this.speechEnabled ? 'enabled' : 'disabled');
    }

    updateSpeechToggleButton() {
        const speechToggle = document.getElementById('speechToggle');
        if (speechToggle) {
            const icon = speechToggle.querySelector('i');
            if (this.speechEnabled) {
                icon.className = 'fas fa-volume-up';
                speechToggle.title = 'Turn off voice (Click to test)';
                speechToggle.classList.remove('btn-outline-secondary');
                speechToggle.classList.add('btn-outline-primary');
            } else {
                icon.className = 'fas fa-volume-mute';
                speechToggle.title = 'Turn on voice';
                speechToggle.classList.remove('btn-outline-primary');
                speechToggle.classList.add('btn-outline-secondary');
            }
        }
    }

    testSpeech() {
        console.log('🧪 Testing speech synthesis...');
        
        if (!this.speechSynthesis) {
            console.error('❌ Speech synthesis not supported');
            alert('Speech synthesis is not supported in this browser');
            return;
        }

        // Test with a simple message
        const testMessage = "Hello! I am your health assistant. Speech is working correctly.";
        
        // Force enable speech for test
        const wasEnabled = this.speechEnabled;
        this.speechEnabled = true;
        
        this.speakMessage(testMessage);
        
        // Restore original state
        setTimeout(() => {
            this.speechEnabled = wasEnabled;
        }, 100);
    }
    
    addErrorMessage(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${message}`;
        this.chatContainer.appendChild(errorDiv);
        this.scrollToBottom();
    }
    
    showTypingIndicator() {
        this.isTyping = true;
        this.typingIndicator.style.display = 'block';
        this.sendButton.disabled = true;
        this.scrollToBottom();
    }
    
    hideTypingIndicator() {
        this.isTyping = false;
        this.typingIndicator.style.display = 'none';
        this.sendButton.disabled = false;
    }
    
    clearChat() {
        if (confirm('Are you sure you want to clear the chat history?')) {
            this.chatContainer.innerHTML = '';
            this.messages = [];
            this.saveChatHistory();
            
            // Show welcome message again
            location.reload();
        }
    }
    
    exportChat() {
        if (this.messages.length === 0) {
            alert('No messages to export.');
            return;
        }
        
        const chatData = this.messages.map(msg => ({
            sender: msg.sender,
            content: msg.content,
            timestamp: msg.timestamp.toISOString()
        }));
        
        const blob = new Blob([JSON.stringify(chatData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `healthbot-chat-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
    
    autoResizeInput() {
        this.messageInput.style.height = 'auto';
        this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 120) + 'px';
    }
    
    scrollToBottom() {
        setTimeout(() => {
            this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
        }, 100);
    }
    
    getCSRFToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return value;
            }
        }
        return '';
    }
    
    getConversationId() {
        return localStorage.getItem('healthbot_conversation_id') || null;
    }
    
    setConversationId(id) {
        localStorage.setItem('healthbot_conversation_id', id);
    }
    
    saveChatHistory() {
        localStorage.setItem('healthbot_chat_history', JSON.stringify(this.messages));
    }
    
    loadChatHistory() {
        const history = localStorage.getItem('healthbot_chat_history');
        if (history) {
            try {
                this.messages = JSON.parse(history);
                // Optionally restore messages to UI
                // this.restoreMessages();
            } catch (e) {
                console.error('Error loading chat history:', e);
            }
        }
    }
    
    restoreMessages() {
        const welcomeMessage = document.querySelector('.welcome-message');
        if (welcomeMessage && this.messages.length > 0) {
            welcomeMessage.style.display = 'none';
        }
        
        this.messages.forEach(msg => {
            this.addMessageToUI(msg.content, msg.sender);
        });
    }
    
    addMessageToUI(content, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'message-avatar';
        avatarDiv.innerHTML = sender === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.innerHTML = this.formatMessage(content);
        
        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(contentDiv);
        
        this.chatContainer.appendChild(messageDiv);
    }
    
    updateStatusIndicator(aiPowered) {
        const statusElement = document.getElementById('statusText');
        const statusContainer = document.getElementById('botStatus');
        
        if (aiPowered) {
            statusElement.textContent = 'AI-Powered & Ready';
            statusContainer.className = 'text-success';
        } else {
            statusElement.textContent = 'Demo Mode - Add API Key';
            statusContainer.className = 'text-warning';
        }
    }
}

// Initialize the chatbot when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new HealthBotChat();
    
    // Add some interactive animations
    animateFeatureCards();
    setupResponsiveNavigation();
});

function animateFeatureCards() {
    const cards = document.querySelectorAll('.feature-card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('animate__animated', 'animate__fadeInUp');
    });
}

function setupResponsiveNavigation() {
    // Mobile sidebar toggle functionality
    const createMobileToggle = () => {
        if (window.innerWidth <= 768) {
            const toggleBtn = document.createElement('button');
            toggleBtn.className = 'btn btn-primary d-md-none position-fixed';
            toggleBtn.style.cssText = 'top: 1rem; left: 1rem; z-index: 1051;';
            toggleBtn.innerHTML = '<i class="fas fa-bars"></i>';
            
            toggleBtn.addEventListener('click', () => {
                document.querySelector('.sidebar').classList.toggle('show');
            });
            
            document.body.appendChild(toggleBtn);
        }
    };
    
    createMobileToggle();
    window.addEventListener('resize', createMobileToggle);
}

// Utility functions for enhanced UX
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} position-fixed`;
    notification.style.cssText = 'top: 1rem; right: 1rem; z-index: 1052; min-width: 300px;';
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
        ${message}
        <button type="button" class="btn-close" aria-label="Close"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        notification.remove();
    }, 5000);
    
    // Close button functionality
    notification.querySelector('.btn-close').addEventListener('click', () => {
        notification.remove();
    });
}

// Health-specific utility functions
function validateHealthInput(input) {
    const healthKeywords = [
        'pain', 'fever', 'headache', 'cough', 'nausea', 'fatigue', 'dizzy',
        'symptoms', 'medication', 'treatment', 'diagnosis', 'health', 'medical'
    ];
    
    return healthKeywords.some(keyword => 
        input.toLowerCase().includes(keyword)
    );
}

function formatHealthResponse(response) {
    // Add health-specific formatting
    response = response.replace(/(IMPORTANT|WARNING|EMERGENCY)/gi, '<strong class="text-danger">$1</strong>');
    response = response.replace(/(NOTE|TIP|ADVICE)/gi, '<strong class="text-info">$1</strong>');
    
    return response;
}