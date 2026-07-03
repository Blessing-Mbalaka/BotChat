// Course Chatbot JavaScript
class CourseChatbot {
    constructor() {
        // Core elements
        this.chatForm = document.getElementById('chat-form');
        this.messageInput = document.getElementById('message-input');
        this.chatMessages = document.getElementById('chat-messages');
        this.clearChatBtn = document.getElementById('clear-chat');
        this.loadingOverlay = document.getElementById('loading-overlay');
        this.loadingMessage = document.getElementById('loading-message');
        
        // Course-specific elements
        this.pdfUploadForm = document.getElementById('pdf-upload-form');
        this.externalSearchToggle = document.getElementById('external-search-toggle');
        this.externalSearchPrompt = document.getElementById('external-search-prompt');
        this.allowExternalBtn = document.getElementById('allow-external');
        this.denyExternalBtn = document.getElementById('deny-external');
        this.historySearchInput = document.getElementById('history-search');
        this.searchHistoryBtn = document.getElementById('search-history-btn');
        this.historyResults = document.getElementById('history-results');
        
        // Speech elements
        this.speechToggle = document.getElementById('speech-toggle');
        this.testVoiceBtn = document.getElementById('test-voice-btn');
        this.speechDebug = document.getElementById('speech-debug');
        
        // State
        this.conversationId = this.generateConversationId();
        this.isLoading = false;
        this.externalSearchEnabled = false;
        this.pendingExternalQuery = null;
        
        // Speech state
        this.speechEnabled = false;
        this.speechSynthesis = window.speechSynthesis;
        this.currentVoice = null;
        this.speechRate = 0.9;
        this.speechPitch = 1.0;
        this.speechVolume = 0.8;
        this.initialLoadMinimumMs = 6000;
        
        this.init();
    }
    
    init() {
        this.showLoading('Preparing your workspace...');
        this.bindEvents();
        this.setupQuickActions();
        this.setupSuggestionChips();
        this.loadCourseStats();
        this.initializeSpeech();
        window.addEventListener('load', () => {
            setTimeout(() => this.hideLoading(), this.initialLoadMinimumMs);
        });
    }
    
    bindEvents() {
        // Chat form submission
        this.chatForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.sendMessage();
        });
        
        // PDF upload form
        this.pdfUploadForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.uploadPDF();
        });
        
        // External search toggle
        this.externalSearchToggle.addEventListener('click', () => {
            this.toggleExternalSearch();
        });
        
        // External search prompt buttons
        this.allowExternalBtn.addEventListener('click', () => {
            this.handleExternalSearchResponse(true);
        });
        
        this.denyExternalBtn.addEventListener('click', () => {
            this.handleExternalSearchResponse(false);
        });
        
        // History search
        this.searchHistoryBtn.addEventListener('click', () => {
            this.searchHistory();
        });
        
        this.historySearchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.searchHistory();
            }
        });
        
        // Speech controls
        this.speechToggle.addEventListener('click', () => {
            this.toggleSpeech();
        });
        
        this.testVoiceBtn.addEventListener('click', () => {
            this.testSpeech();
        });
        
        // Clear chat
        this.clearChatBtn.addEventListener('click', () => {
            this.clearChat();
        });
        
        // Auto-resize textarea
        this.messageInput.addEventListener('input', () => {
            this.autoResizeTextarea();
        });
        
        // Enter key handling
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
    }
    
    initializeSpeech() {
        console.log('🎤 Initializing speech synthesis...');
        console.log('🎤 speechSynthesis available:', !!this.speechSynthesis);
        
        if (!this.speechSynthesis) {
            console.log('🔇 Speech synthesis not supported');
            this.speechDebug.textContent = 'Speech not supported in this browser';
            return;
        }
        
        // Wait for voices to load
        const loadVoices = () => {
            const voices = this.speechSynthesis.getVoices();
            console.log('🎤 Available voices:', voices.length);
            
            if (voices.length === 0) {
                setTimeout(loadVoices, 100);
                return;
            }
            
            // Find best female voice
            this.selectBestVoice(voices);
            this.speechDebug.textContent = `Voice: ${this.currentVoice?.name || 'Default'}`;
        };
        
        if (this.speechSynthesis.getVoices().length === 0) {
            this.speechSynthesis.addEventListener('voiceschanged', loadVoices);
        } else {
            loadVoices();
        }
    }
    
    selectBestVoice(voices) {
        const femaleVoices = [
            'Microsoft Zira Desktop - English (United States)',
            'Google US English (Female)',
            'Microsoft Susan',
            'Apple Samantha',
            'Google UK English Female',
            'Microsoft Hazel Desktop'
        ];
        
        // Try to find preferred female voices
        for (const preferredName of femaleVoices) {
            const voice = voices.find(v => v.name.includes(preferredName.split(' ')[1]) || v.name === preferredName);
            if (voice) {
                this.currentVoice = voice;
                console.log('🎤 Selected voice:', voice.name);
                return;
            }
        }
        
        // Fallback to any female voice
        const femaleVoice = voices.find(voice => 
            voice.name.toLowerCase().includes('female') ||
            voice.name.toLowerCase().includes('woman') ||
            (voice.name.toLowerCase().includes('english') && voice.gender === 'female')
        );
        
        if (femaleVoice) {
            this.currentVoice = femaleVoice;
            console.log('🎤 Selected fallback female voice:', femaleVoice.name);
        } else {
            this.currentVoice = voices[0];
            console.log('🎤 Selected default voice:', voices[0]?.name);
        }
    }
    
    toggleSpeech() {
        this.speechEnabled = !this.speechEnabled;
        const statusText = this.speechEnabled ? 'ON' : 'OFF';
        const statusIcon = this.speechEnabled ? 'fa-volume-up' : 'fa-volume-mute';
        
        document.getElementById('speech-status').textContent = `Speech: ${statusText}`;
        this.speechToggle.querySelector('i').className = `fas ${statusIcon}`;
        
        if (this.speechEnabled) {
            this.speechToggle.classList.add('active');
        } else {
            this.speechToggle.classList.remove('active');
            this.speechSynthesis.cancel(); // Stop any current speech
        }
        
        console.log('🎤 Speech toggled:', this.speechEnabled);
    }
    
    testSpeech() {
        const testMessage = "Hello! I'm your CourseBot AI assistant. I can help you with your educational materials and curriculum content.";
        this.speakMessage(testMessage, true); // Force speak for testing
    }
    
    speakMessage(message, force = false) {
        console.log('🎤 speakMessage called with enabled:', this.speechEnabled || force);
        
        if (!this.speechEnabled && !force) {
            console.log('🔇 Speech disabled by user');
            return;
        }
        
        if (!this.speechSynthesis) {
            console.log('🔇 Speech synthesis not available');
            return;
        }
        
        // Clean message for speech
        const cleanMessage = this.cleanMessageForSpeech(message);
        console.log('🎤 Speaking:', cleanMessage.substring(0, 100) + '...');
        
        const utterance = new SpeechSynthesisUtterance(cleanMessage);
        utterance.voice = this.currentVoice;
        utterance.rate = this.speechRate;
        utterance.pitch = this.speechPitch;
        utterance.volume = this.speechVolume;
        
        utterance.onstart = () => {
            console.log('🎤 Speech started');
            this.speechDebug.textContent = 'Speaking...';
        };
        
        utterance.onend = () => {
            console.log('🎤 Speech ended');
            this.speechDebug.textContent = `Voice: ${this.currentVoice?.name || 'Default'}`;
        };
        
        utterance.onerror = (event) => {
            console.error('🎤 Speech error:', event.error);
            this.speechDebug.textContent = `Speech error: ${event.error}`;
        };
        
        this.speechSynthesis.speak(utterance);
    }
    
    cleanMessageForSpeech(message) {
        return message
            .replace(/<[^>]*>/g, ' ')
            .replace(/\*\*(.*?)\*\*/g, '$1')
            .replace(/\*(.*?)\*/g, '$1')
            .replace(/#{1,6}\s/g, '')
            .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
            .replace(/📚|🎓|💡|⚠️|✅|❌|🔍|📄|🎤|🔇|🌐/g, '')
            .replace(/\s+/g, ' ')
            .trim();
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
    
    handleQuickAction(action) {
        const actions = {
            'summary': 'Please provide a summary of the key concepts from my uploaded course materials.',
            'key-concepts': 'What are the main key concepts I should focus on from my course materials?',
            'quiz': 'Create some practice questions based on my uploaded course content.',
            'assignments': 'What types of assignments or exercises can I work on based on my course materials?'
        };
        
        if (actions[action]) {
            this.messageInput.value = actions[action];
            this.sendMessage();
        }
    }
    
    setupSuggestionChips() {
        const suggestionChips = document.querySelectorAll('.suggestion-chip');
        suggestionChips.forEach(chip => {
            chip.addEventListener('click', () => {
                const suggestion = chip.dataset.suggestion;
                this.messageInput.value = suggestion;
                this.messageInput.focus();
            });
        });
    }
    
    toggleExternalSearch() {
        this.externalSearchEnabled = !this.externalSearchEnabled;
        const statusText = this.externalSearchEnabled ? 'ON' : 'OFF';
        document.getElementById('external-status').textContent = `External: ${statusText}`;
        
        if (this.externalSearchEnabled) {
            this.externalSearchToggle.classList.add('active');
        } else {
            this.externalSearchToggle.classList.remove('active');
        }
    }
    
    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message || this.isLoading) return;
        
        // Add user message to chat
        this.addMessage(message, 'user');
        this.messageInput.value = '';
        this.autoResizeTextarea();
        
        // Show loading
        this.showLoading('Preparing your workspace...');
        
        try {
            const response = await fetch('/course/chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    message: message,
                    conversation_id: this.conversationId,
                    request_external: this.externalSearchEnabled
                })
            });
            
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error || 'Failed to get response');
            }
            
            // Get the response message (support both 'response' and 'message' keys)
            const responseMessage = data.message || data.response || '';
            
            // Add bot response
            this.addMessage(responseMessage, 'bot');
            
            // Handle visualizations if present
            if (data.visualizations && Array.isArray(data.visualizations) && data.visualizations.length > 0) {
                for (const viz of data.visualizations) {
                    this.renderVisualization(viz);
                }
            }
            
            // Check if external search is needed and not already enabled
            if (data.needs_external_search && !this.externalSearchEnabled) {
                this.showExternalSearchPrompt(message);
            }
            
            // Show source information if available
            if (data.sources && data.sources.length > 0) {
                this.addSourceInfo(data.sources);
            }
            
            // Update conversation ID
            this.conversationId = data.conversation_id;
            
            // Speak the response
            this.speakMessage(responseMessage);
            
        } catch (error) {
            console.error('Error sending message:', error);
            this.addMessage('I encountered an error processing your educational query. Please try again.', 'bot');
        } finally {
            this.hideLoading();
        }
    }
    
    showExternalSearchPrompt(originalQuery) {
        this.pendingExternalQuery = originalQuery;
        this.externalSearchPrompt.style.display = 'block';
        
        // Auto-hide after 10 seconds
        setTimeout(() => {
            if (this.externalSearchPrompt.style.display === 'block') {
                this.externalSearchPrompt.style.display = 'none';
                this.pendingExternalQuery = null;
            }
        }, 10000);
    }
    
    async handleExternalSearchResponse(allowed) {
        this.externalSearchPrompt.style.display = 'none';
        
        if (allowed && this.pendingExternalQuery) {
            // Enable external search and retry the query
            this.externalSearchEnabled = true;
            this.toggleExternalSearch();
            
            // Retry the query with external search enabled
            this.messageInput.value = this.pendingExternalQuery;
            this.sendMessage();
        }
        
        this.pendingExternalQuery = null;
    }
    
    async uploadPDF() {
        const fileInput = document.getElementById('pdf-file');
        const courseNameInput = document.getElementById('course-name');
        const uploadStatus = document.getElementById('upload-status');
        
        const file = fileInput.files[0];
        if (!file) {
            this.showUploadStatus('Please select a PDF file.', 'danger');
            return;
        }
        
        const formData = new FormData();
        formData.append('pdf_file', file);
        formData.append('course_name', courseNameInput.value || 'General Course');
        
        this.showLoading('Preparing your workspace...');
        this.showUploadStatus('Uploading and processing PDF...', 'info');
        
        try {
            const response = await fetch('/course/upload/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: formData
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showUploadStatus(data.message, 'success');
                this.loadCourseStats(); // Refresh stats
                
                // Reset form
                fileInput.value = '';
                courseNameInput.value = '';
                
                // Add confirmation message to chat
                this.addMessage(`✅ PDF "${file.name}" has been successfully uploaded and processed. You can now ask questions about this course material!`, 'bot');
            } else {
                this.showUploadStatus(data.error, 'danger');
            }
            
        } catch (error) {
            console.error('Error uploading PDF:', error);
            this.showUploadStatus('Error uploading file. Please try again.', 'danger');
        } finally {
            this.hideLoading();
        }
    }
    
    showUploadStatus(message, type) {
        const uploadStatus = document.getElementById('upload-status');
        uploadStatus.innerHTML = `<div class="alert alert-${type}">${message}</div>`;
        
        // Auto-hide success messages
        if (type === 'success') {
            setTimeout(() => {
                uploadStatus.innerHTML = '';
            }, 5000);
        }
    }
    
    async loadCourseStats() {
        try {
            const response = await fetch('/course/stats/');
            const data = await response.json();
            
            if (data.success) {
                document.getElementById('document-count').textContent = data.stats.total_documents || 0;
                document.getElementById('conversation-count').textContent = data.stats.conversation_history || 0;
            }
        } catch (error) {
            console.error('Error loading course stats:', error);
        }
    }
    
    async searchHistory() {
        const query = this.historySearchInput.value.trim();
        if (!query) return;
        
        try {
            const response = await fetch('/course/history/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({ query })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.displayHistoryResults(data.results);
            }
        } catch (error) {
            console.error('Error searching history:', error);
        }
    }
    
    displayHistoryResults(results) {
        const container = this.historyResults;
        
        if (results.length === 0) {
            container.innerHTML = '<div class="text-muted small">No matching conversations found.</div>';
            return;
        }
        
        container.innerHTML = results.map(result => `
            <div class="history-item" data-query="${result.query}">
                <div class="history-item-query">${result.query}</div>
                <div class="history-item-time">${new Date(result.timestamp).toLocaleString()}</div>
            </div>
        `).join('');
        
        // Add click handlers to history items
        container.querySelectorAll('.history-item').forEach(item => {
            item.addEventListener('click', () => {
                const query = item.dataset.query;
                this.messageInput.value = query;
                this.messageInput.focus();
            });
        });
    }
    
    addMessage(content, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'message-avatar';
        avatarDiv.innerHTML = sender === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-graduation-cap"></i>';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        const headerDiv = document.createElement('div');
        headerDiv.className = 'message-header';
        headerDiv.innerHTML = `
            <span class="sender-name">${sender === 'user' ? 'You' : 'CourseBot AI'}</span>
            <span class="message-time" data-time="now"></span>
        `;
        
        const textDiv = document.createElement('div');
        textDiv.className = 'message-text';
        textDiv.innerHTML = this.formatMessage(content);
        
        contentDiv.appendChild(headerDiv);
        contentDiv.appendChild(textDiv);
        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(contentDiv);
        
        this.chatMessages.appendChild(messageDiv);
        this.updateMessageTimes();
        this.scrollToBottom();
    }
    
    addSourceInfo(sources) {
        if (sources.length === 0) return;
        
        const sourceDiv = document.createElement('div');
        sourceDiv.className = 'message bot-message';
        sourceDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-graduation-cap"></i>
            </div>
            <div class="message-content">
                <div class="message-header">
                    <span class="sender-name">CourseBot AI</span>
                    <span class="message-time" data-time="now"></span>
                </div>
                <div class="message-text">
                    📚 <strong>Sources from your course materials:</strong><br><br>
                    ${sources.map((source, index) => `
                        <div class="source-indicator">
                            <i class="fas fa-file-pdf"></i>
                            <strong>${source.course_name}</strong> (${Math.round(source.similarity * 100)}% match)
                        </div>
                        <div class="small text-muted mb-2">${source.content_preview}</div>
                    `).join('')}
                </div>
            </div>
        `;
        
        this.chatMessages.appendChild(sourceDiv);
        this.scrollToBottom();
    }
    
    formatMessage(message) {
        // Safety check: ensure message is a string
        if (!message || typeof message !== 'string') {
            message = String(message || '');
        }
        
        // Convert line breaks
        message = message.replace(/\n/g, '<br>');
        
        // Format bold text
        message = message.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Format italic text
        message = message.replace(/\*(.*?)\*/g, '<em>$1</em>');
        
        // Format educational links
        message = message.replace(/\[([^\[\]]+)\]\(([^()]+)\)/g, 
            '<a href="$2" target="_blank" rel="noopener noreferrer" class="educational-link">$1 <i class="fas fa-external-link-alt" style="font-size: 0.8em;"></i></a>');
        
        // Format section headers
        message = message.replace(/(📚|🎓|💡|⚠️|✅) \*\*(.*?)\*\*/g, '<div class="course-highlight">$1 <strong>$2</strong></div>');
        
        return message;
    }
    
    autoResizeTextarea() {
        const textarea = this.messageInput;
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }
    
    showLoading() {
        let message = 'Preparing your workspace...';
        if (arguments.length > 0 && arguments[0]) {
            message = arguments[0];
        }
        this.isLoading = true;
        if (this.loadingMessage) {
            this.loadingMessage.textContent = message;
        }
        this.loadingOverlay.classList.remove('fade-out');
        this.loadingOverlay.classList.add('visible');
    }
    
    hideLoading() {
        this.isLoading = false;
        this.loadingOverlay.classList.remove('visible');
        this.loadingOverlay.classList.add('fade-out');
    }
    
    clearChat() {
        this.chatMessages.innerHTML = `
            <div class="message bot-message">
                <div class="message-avatar">
                    <i class="fas fa-graduation-cap"></i>
                </div>
                <div class="message-content">
                    <div class="message-header">
                        <span class="sender-name">CourseBot AI</span>
                        <span class="message-time" data-time="now"></span>
                    </div>
                    <div class="message-text">
                        👋 <strong>Welcome back to CourseBot AI!</strong><br><br>
                        I'm ready to help you with your course materials and educational content.<br><br>
                        Upload your PDFs using the sidebar or ask me questions about your existing course materials.
                    </div>
                </div>
            </div>
        `;
        this.updateMessageTimes();
        this.conversationId = this.generateConversationId();
    }
    
    updateMessageTimes() {
        const timeElements = document.querySelectorAll('[data-time="now"]');
        const now = new Date();
        const timeString = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        timeElements.forEach(element => {
            element.textContent = timeString;
            element.removeAttribute('data-time');
        });
    }
    
    scrollToBottom() {
        setTimeout(() => {
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        }, 100);
    }

    renderVisualization(vizConfig) {
        /**
         * Render a visualization from LLM-generated configuration.
         * Supports: table, bar, pie, line, area, scatter, donut
         */
        try {
            if (!vizConfig || !vizConfig.type) {
                console.warn('Invalid visualization config:', vizConfig);
                return;
            }

            const vizType = vizConfig.type.toLowerCase();
            const data = vizConfig.data || {};
            const columns = data.columns || [];
            const rows = data.rows || [];

            if (!columns || !rows || columns.length === 0) {
                console.warn('Visualization missing data:', vizConfig);
                return;
            }

            // Route to appropriate renderer
            switch (vizType) {
                case 'table':
                    this.renderVisualizationTable(vizConfig);
                    break;
                case 'bar':
                    this.renderVisualizationChart(vizConfig, 'bar');
                    break;
                case 'pie':
                    this.renderVisualizationChart(vizConfig, 'pie');
                    break;
                case 'line':
                    this.renderVisualizationChart(vizConfig, 'line');
                    break;
                case 'area':
                    this.renderVisualizationChart(vizConfig, 'line', true); // area uses line with fill
                    break;
                case 'scatter':
                    this.renderVisualizationChart(vizConfig, 'scatter');
                    break;
                case 'donut':
                    this.renderVisualizationChart(vizConfig, 'doughnut');
                    break;
                default:
                    console.warn('Unknown visualization type:', vizType);
            }
        } catch (error) {
            console.error('Error rendering visualization:', error);
            this.addMessage(`Error rendering visualization: ${error.message}`, 'bot');
        }
    }

    renderVisualizationTable(vizConfig) {
        /**
         * Render tabular data as an HTML table
         */
        try {
            const esc = (s) => this.escapeHtml(s == null ? '' : s);
            const data = vizConfig.data || {};
            const columns = data.columns || [];
            const rows = (data.rows || []).slice(0, 50); // Limit to 50 rows
            const title = esc(vizConfig.title || 'Data Table');
            const tableId = `table-viz-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
            const downloadBtnId = `download-${tableId}`;
            
            // Build table HTML
            const thead = '<thead><tr>' + columns.map(c => `<th>${esc(c)}</th>`).join('') + '</tr></thead>';
            const tbody = '<tbody>' + rows.map(row => 
                '<tr>' + row.map(cell => `<td>${esc(cell)}</td>`).join('') + '</tr>'
            ).join('') + '</tbody>';
            
            const source = vizConfig.source ? `<div class="course-viz-meta">Source: ${esc(vizConfig.source === 'extracted' ? 'Course Materials' : 'AI Generated')}</div>` : '';
            
            const html = `<div class="message bot-message">
                <div class="message-avatar">
                    <i class="fas fa-graduation-cap"></i>
                </div>
                <div class="message-content">
                    <div class="course-viz-table" id="${tableId}">
                        <div class="course-viz-title-bar">
                            <div class="course-viz-title">${title}</div>
                            <button id="${downloadBtnId}" class="btn-download-course" title="Download as PNG">
                                <i class="fas fa-download"></i> PNG
                            </button>
                        </div>
                        ${source}
                        <table class="table table-sm table-striped">
                            ${thead}
                            ${tbody}
                        </table>
                    </div>
                </div>
            </div>`;
            
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = html;
            this.chatMessages.appendChild(tempDiv.firstElementChild);

            // Attach download handler
            setTimeout(() => {
                const downloadBtn = document.getElementById(downloadBtnId);
                if (downloadBtn) {
                    downloadBtn.addEventListener('click', () => {
                        this.downloadTableAsPNG(tableId, title);
                    });
                }
            }, 100);
            
            this.scrollToBottom();

        } catch (error) {
            console.error('Error rendering table:', error);
        }
    }

    renderVisualizationChart(vizConfig, chartType, isArea = false) {
        /**
         * Render data as a Chart.js chart
         */
        try {
            if (typeof Chart === 'undefined') {
                this.addMessage('Chart.js not loaded; unable to render chart.', 'bot');
                return;
            }

            const esc = (s) => this.escapeHtml(s == null ? '' : s);
            const data = vizConfig.data || {};
            const columns = Array.isArray(data.columns) ? data.columns : [];
            const rows = Array.isArray(data.rows) ? data.rows : [];
            const title = esc(vizConfig.title || 'Chart');
            const canvasId = `chart-viz-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
            const downloadBtnId = `download-${canvasId}`;
            
            // Safety check: ensure we have data
            if (!columns || columns.length === 0 || !rows || rows.length === 0) {
                this.addMessage('No data available for visualization.', 'bot');
                return;
            }
            
            // Prepare data for Chart.js
            let labels = [];
            let datasets = [];

            if (chartType === 'pie' || chartType === 'doughnut') {
                // For pie/donut: first column is labels, second is values
                if (columns && columns.length >= 2 && rows && rows.length > 0) {
                    labels = rows.map(row => esc(row && row[0] ? row[0] : ''));
                    const values = rows.map(row => {
                        const val = parseFloat(row && row[1] ? row[1] : 0);
                        return isNaN(val) ? 0 : val;
                    });
                    
                    const colors = [
                        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', 
                        '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF'
                    ];
                    
                    datasets.push({
                        label: columns[1] || 'Value',
                        data: values,
                        backgroundColor: colors.slice(0, values.length),
                        borderColor: '#fff',
                        borderWidth: 2
                    });
                }
            } else if (chartType === 'scatter') {
                // For scatter: x and y coordinates
                if (columns && columns.length >= 2 && rows && rows.length > 0) {
                    const points = rows.map(row => ({
                        x: parseFloat((row && row[0]) ? row[0] : 0) || 0,
                        y: parseFloat((row && row[1]) ? row[1] : 0) || 0
                    }));
                    
                    datasets.push({
                        label: (columns && columns[1]) || 'Value',
                        data: points,
                        backgroundColor: '#36A2EB',
                        borderColor: '#36A2EB'
                    });
                }
            } else {
                // For bar, line: first column is labels, rest are data series
                if (rows && rows.length > 0) {
                    labels = rows.map(row => esc((row && row[0]) ? row[0] : ''));
                    
                    const colors = [
                        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', 
                        '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF'
                    ];
                
                    // Create dataset for each numeric column
                    if (columns && columns.length > 1) {
                        for (let i = 1; i < columns.length && i < 5; i++) {
                            const values = rows.map(row => {
                                const val = parseFloat((row && row[i]) ? row[i] : 0);
                                return isNaN(val) ? 0 : val;
                            });
                            
                            datasets.push({
                                label: (columns && columns[i]) || `Series ${i}`,
                                data: values,
                                borderColor: colors[i - 1],
                                backgroundColor: isArea ? colors[i - 1] + '33' : (chartType === 'bar' ? colors[i - 1] : colors[i - 1] + '33'),
                                borderWidth: 2,
                                fill: isArea,
                                tension: chartType === 'line' || isArea ? 0.3 : 0
                            });
                        }
                    }
                }
            }

            // Build container with download button
            const source = vizConfig.source ? `<div class="course-viz-meta">Source: ${esc(vizConfig.source === 'extracted' ? 'Course Materials' : 'AI Generated')}</div>` : '';
            const html = `<div class="message bot-message">
                <div class="message-avatar">
                    <i class="fas fa-graduation-cap"></i>
                </div>
                <div class="message-content">
                    <div class="course-viz-chart">
                        <div class="course-viz-title-bar">
                            <div class="course-viz-title">${title}</div>
                            <button id="${downloadBtnId}" class="btn-download-course" title="Download as PNG">
                                <i class="fas fa-download"></i> PNG
                            </button>
                        </div>
                        ${source}
                        <div style="position: relative; width: 100%; height: 300px;">
                            <canvas id="${canvasId}" width="400" height="300"></canvas>
                        </div>
                    </div>
                </div>
            </div>`;
            
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = html;
            this.chatMessages.appendChild(tempDiv.firstElementChild);

            // Create Chart.js instance
            setTimeout(() => {
                const ctx = document.getElementById(canvasId);
                if (!ctx) {
                    console.error('Canvas element not found:', canvasId);
                    return;
                }

                const config = {
                    type: chartType,
                    data: {
                        labels: labels || [],
                        datasets: datasets || []
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { display: datasets && datasets.length > 1, position: 'top' },
                            title: { display: false }
                        },
                        scales: chartType !== 'pie' && chartType !== 'doughnut' ? {
                            y: { beginAtZero: true },
                            x: { display: true }
                        } : {}
                    }
                };

                if (!window.courseChartInstances) {
                    window.courseChartInstances = {};
                }

                if (window.courseChartInstances[canvasId]) {
                    window.courseChartInstances[canvasId].destroy();
                }

                window.courseChartInstances[canvasId] = new Chart(ctx, config);

                // Attach download handler
                const downloadBtn = document.getElementById(downloadBtnId);
                if (downloadBtn) {
                    downloadBtn.addEventListener('click', () => {
                        this.downloadChartAsPNG(canvasId, title);
                    });
                }
            }, 100);

            this.scrollToBottom();

        } catch (error) {
            console.error('Error rendering chart:', error);
            this.addMessage(`Error rendering chart: ${error.message}`, 'bot');
        }
    }

    downloadChartAsPNG(canvasId, title) {
        /**
         * Download a chart as PNG
         */
        try {
            const canvas = document.getElementById(canvasId);
            if (!canvas) {
                console.error('Canvas not found:', canvasId);
                return;
            }

            // Create a temporary canvas with white background
            const tempCanvas = document.createElement('canvas');
            const rect = canvas.getBoundingClientRect();
            tempCanvas.width = canvas.width;
            tempCanvas.height = canvas.height;

            const tempCtx = tempCanvas.getContext('2d');
            // Fill with white background
            tempCtx.fillStyle = 'white';
            tempCtx.fillRect(0, 0, tempCanvas.width, tempCanvas.height);
            
            // Copy the chart canvas to temp canvas
            tempCtx.drawImage(canvas, 0, 0);

            // Download
            const link = document.createElement('a');
            link.href = tempCanvas.toDataURL('image/png');
            link.download = `${title.replace(/\s+/g, '_')}_${Date.now()}.png`;
            link.click();
        } catch (error) {
            console.error('Error downloading chart:', error);
            this.addMessage(`Error downloading chart: ${error.message}`, 'bot');
        }
    }

    downloadTableAsPNG(tableId, title) {
        /**
         * Download a table as PNG using html2canvas
         */
        try {
            const tableElement = document.getElementById(tableId);
            if (!tableElement) {
                console.error('Table not found:', tableId);
                return;
            }

            // Check if html2canvas is available
            if (typeof html2canvas === 'undefined') {
                this.createTableImageFallback(tableElement, title);
                return;
            }

            // Use html2canvas if available
            html2canvas(tableElement, {
                backgroundColor: '#ffffff',
                scale: 2
            }).then(canvas => {
                const link = document.createElement('a');
                link.href = canvas.toDataURL('image/png');
                link.download = `${title.replace(/\s+/g, '_')}_${Date.now()}.png`;
                link.click();
            }).catch(error => {
                console.error('html2canvas error:', error);
                this.createTableImageFallback(tableElement, title);
            });

        } catch (error) {
            console.error('Error downloading table:', error);
            this.addMessage(`Error downloading table: ${error.message}`, 'bot');
        }
    }

    createTableImageFallback(tableElement, title) {
        /**
         * Fallback method to create table image without html2canvas
         */
        try {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            
            // Get table dimensions
            const tableClone = tableElement.cloneNode(true);
            tableClone.style.position = 'fixed';
            tableClone.style.left = '-9999px';
            tableClone.style.top = '-9999px';
            tableClone.style.visibility = 'hidden';
            document.body.appendChild(tableClone);
            
            const width = tableClone.offsetWidth + 40;
            const height = tableClone.offsetHeight + 40;
            
            canvas.width = width;
            canvas.height = height;
            
            // Setup context
            ctx.fillStyle = '#ffffff';
            ctx.fillRect(0, 0, width, height);
            
            // Draw title
            ctx.fillStyle = '#000000';
            ctx.font = 'bold 16px Arial';
            ctx.fillText(title, 20, 25);
            
            // Draw table border
            ctx.strokeStyle = '#cccccc';
            ctx.lineWidth = 1;
            ctx.strokeRect(20, 40, Math.min(width - 40, 500), Math.min(height - 60, 400));
            
            document.body.removeChild(tableClone);
            
            // Download canvas
            const link = document.createElement('a');
            link.href = canvas.toDataURL('image/png');
            link.download = `${title.replace(/\s+/g, '_')}_${Date.now()}.png`;
            link.click();
        } catch (error) {
            console.error('Fallback image creation error:', error);
            this.addMessage('Unable to download table. Try using a modern browser.', 'bot');
        }
    }

    escapeHtml(value) {
        return String(value)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }
    
    generateConversationId() {
        return 'course_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
    
    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
               document.querySelector('meta[name=csrf-token]')?.getAttribute('content') || '';
    }
}

// Initialize the course chatbot when the page loads
document.addEventListener('DOMContentLoaded', () => {
    window.courseChatbot = new CourseChatbot();
});
