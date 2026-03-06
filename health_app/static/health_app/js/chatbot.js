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
        this.artifactStore = new Map();
        this.chartInstances = {};

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
        this.setupFileUpload();
        this.setupKpiPanel();
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

    setupFileUpload() {
        const fileInput = document.getElementById('fileUpload');
        if (!fileInput) return;
        fileInput.addEventListener('change', async (e) => {
            const file = e.target.files[0];
            if (!file) return;
            this.addSystemMessage(`Uploading ${file.name} for extraction...`);
            const form = new FormData();
            form.append('file', file);
            try {
                const res = await fetch('/api/extract/', {
                    method: 'POST',
                    body: form,
                    headers: {
                        'X-CSRFToken': this.getCSRFToken(),
                    },
                });
                const data = await res.json();
                if (!data.success) throw new Error(data.error || 'Extraction failed');
                this.renderArtifacts(data.artifacts || []);
                if ((data.warnings||[]).length) {
                    this.addSystemMessage('Warnings: ' + data.warnings.join('; '));
                }
            } catch (err) {
                this.addSystemMessage('Extraction error: ' + err.message);
            } finally {
                fileInput.value = '';
            }
        });
    }

    renderArtifacts(artifacts) {
        if (!Array.isArray(artifacts)) return;
        let rendered = 0;
        artifacts.forEach(artifact => {
            if (!artifact || !artifact.id) return;
            this.artifactStore.set(artifact.id, artifact);
            if (artifact.type === 'table') {
                const html = this.tableToHTML(artifact);
                this.addRichMessage(html, 'bot');
                rendered += 1;
            } else if (artifact.type === 'chart') {
                this.renderChart(artifact);
                rendered += 1;
            }
        });
        if (!rendered) {
            this.addSystemMessage('No tables or charts detected in that file.');
        } else {
            this.updateKpiTableOptions();
        }
    }

    tableToHTML(t) {
        const esc = (s) => this.escapeHtml(s == null ? '' : s);
        const head = '<thead><tr>' + (t.columns || []).map(c=>`<th>${esc(c)}</th>`).join('') + '</tr></thead>';
        const bodyRows = (t.rows||[]).slice(0,50).map(r=>'<tr>'+r.map(c=>`<td>${esc(c)}</td>`).join('')+'</tr>').join('');
        const body = `<tbody>${bodyRows}</tbody>`;
        const source = t.source ? `<div class="artifact-meta">Source: ${esc(t.source.name || t.source.type || 'upload')}</div>` : '';
        return `<div class="artifact-table"><div class="artifact-title">${esc(t.title || 'Table')}</div>${source}<table>${head}${body}</table></div>`;
    }

    renderChart(chart) {
        if (typeof Chart === 'undefined') {
            this.addSystemMessage('Chart.js not loaded; unable to render chart.');
            return;
        }
        const esc = (s) => this.escapeHtml(s == null ? '' : s);
        const canvasId = `chart-${chart.id}-${Date.now()}`;
        const title = esc(chart.title || 'Chart');
        const meta = chart.source ? `<div class="artifact-meta">Source: ${esc(chart.source.name || chart.source.type || 'upload')}</div>` : '';
        const container = `<div class="artifact-chart"><div class="artifact-title">${title}</div>${meta}<canvas id="${canvasId}" height="240"></canvas></div>`;
        this.addRichMessage(container, 'bot');
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;
        const palette = ['#2c7be5', '#00d2d3', '#34a853', '#fbbc04', '#ea4335', '#6f42c1'];
        const dataset = (chart.series || []).map((serie, idx) => {
            const color = palette[idx % palette.length];
            return {
                label: serie.name || `Series ${idx+1}`,
                data: serie.data || [],
                borderWidth: 2,
                borderColor: color,
                backgroundColor: chart.chart_type === 'bar' ? color + '55' : color,
                fill: chart.chart_type === 'line' ? false : true,
            };
        });
        const config = {
            type: (chart.chart_type || 'bar'),
            data: {
                labels: chart.categories || [],
                datasets: dataset,
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'top' },
                    title: { display: false },
                },
                scales: {
                    y: { beginAtZero: true },
                },
            },
        };
        if (this.chartInstances[canvasId]) {
            this.chartInstances[canvasId].destroy();
        }
        this.chartInstances[canvasId] = new Chart(ctx, config);
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
            this.addSystemMessage(`Error rendering visualization: ${error.message}`);
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
            
            const source = vizConfig.source ? `<div class="artifact-meta">Source: ${esc(vizConfig.source === 'extracted' ? 'Uploaded Data' : 'AI Generated')}</div>` : '';
            
            const html = `<div class="artifact-table" id="${tableId}">
                <div class="artifact-title-bar">
                    <div class="artifact-title">${title}</div>
                    <button id="${downloadBtnId}" class="btn-download-chart" title="Download as PNG">
                        <i class="fas fa-download"></i> PNG
                    </button>
                </div>
                ${source}
                <table class="table table-sm table-striped">
                    ${thead}
                    ${tbody}
                </table>
            </div>`;
            
            this.addRichMessage(html, 'bot');

            // Attach download handler
            setTimeout(() => {
                const downloadBtn = document.getElementById(downloadBtnId);
                if (downloadBtn) {
                    downloadBtn.addEventListener('click', () => {
                        this.downloadTableAsPNG(tableId, title);
                    });
                }
            }, 100);

        } catch (error) {
            console.error('Error rendering table:', error);
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
                // Fallback: use canvas rendering without html2canvas
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');
                
                // Basic table to canvas conversion
                const width = tableElement.offsetWidth;
                const height = tableElement.offsetHeight;
                
                canvas.width = width * 2; // 2x for better quality
                canvas.height = height * 2;
                
                ctx.scale(2, 2);
                ctx.fillStyle = 'white';
                ctx.fillRect(0, 0, width, height);
                
                // Try to render HTML using a workaround
                const cloned = tableElement.cloneNode(true);
                cloned.style.position = 'absolute';
                cloned.style.left = '-9999px';
                document.body.appendChild(cloned);
                
                // Fallback: just create a text-based image
                this.createTableImageFallback(tableElement, title);
                document.body.removeChild(cloned);
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
            this.addSystemMessage(`Error downloading table: ${error.message}`);
        }
    }

    createTableImageFallback(tableElement, title) {
        /**
         * Fallback method to create table image without html2canvas
         * Converts table to a canvas-based image
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
            this.addSystemMessage('Unable to download table. Try using a modern browser.');
        }
    }

    renderVisualizationChart(vizConfig, chartType, isArea = false) {
        /**
         * Render data as a Chart.js chart
         */
        try {
            if (typeof Chart === 'undefined') {
                this.addSystemMessage('Chart.js not loaded; unable to render chart.');
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
                this.addSystemMessage('No data available for visualization.');
                return;
            }
            
            // Prepare data for Chart.js
            let labels = [];
            let datasets = [];

            if (chartType === 'pie' || chartType === 'doughnut') {
                // For pie/donut: first column is labels, second is values
                if (columns.length >= 2 && rows && rows.length > 0) {
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
            const source = vizConfig.source ? `<div class="artifact-meta">Source: ${esc(vizConfig.source === 'extracted' ? 'Uploaded Data' : 'AI Generated')}</div>` : '';
            const container = `<div class="artifact-chart">
                <div class="artifact-title-bar">
                    <div class="artifact-title">${title}</div>
                    <button id="${downloadBtnId}" class="btn-download-chart" title="Download as PNG">
                        <i class="fas fa-download"></i> PNG
                    </button>
                </div>
                ${source}
                <div style="position: relative; width: 100%; height: 300px;">
                    <canvas id="${canvasId}" width="400" height="300"></canvas>
                </div>
            </div>`;
            
            this.addRichMessage(container, 'bot');

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

                if (this.chartInstances[canvasId]) {
                    this.chartInstances[canvasId].destroy();
                }

                this.chartInstances[canvasId] = new Chart(ctx, config);

                // Attach download handler
                const downloadBtn = document.getElementById(downloadBtnId);
                if (downloadBtn) {
                    downloadBtn.addEventListener('click', () => {
                        this.downloadChartAsPNG(canvasId, title);
                    });
                }
            }, 100);

        } catch (error) {
            console.error('Error rendering chart:', error);
            this.addSystemMessage(`Error rendering chart: ${error.message}`);
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

            // Get the parent container for a clean download
            const parentDiv = canvas.closest('.artifact-chart');
            if (!parentDiv) {
                console.error('Parent container not found');
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
            this.addSystemMessage(`Error downloading chart: ${error.message}`);
        }
    }

    addRichMessage(content, sender = 'bot') {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message rich-message`;

        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'message-avatar';
        avatarDiv.innerHTML = sender === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.innerHTML = content;

        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(contentDiv);
        this.chatContainer.appendChild(messageDiv);

        this.messages.push({ content, sender, timestamp: new Date(), type: 'html' });
        this.saveChatHistory();
        this.scrollToBottom();
    }

    addSystemMessage(message) {
        const html = `<div class="system-message"><i class="fas fa-info-circle"></i> ${this.escapeHtml(message)}</div>`;
        this.addRichMessage(html, 'bot');
    }

    escapeHtml(value) {
        return String(value)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    setupKpiPanel() {
        const toggleBtn = document.getElementById('toggleKpi');
        const panel = document.getElementById('kpiPanel');
        const runBtn = document.getElementById('runKpiBtn');
        const closeBtn = document.getElementById('closeKpiBtn');
        if (!toggleBtn || !panel) return;

        toggleBtn.addEventListener('click', () => {
            const isHidden = panel.style.display === 'none' || panel.style.display === '';
            panel.style.display = isHidden ? 'block' : 'none';
            if (isHidden) {
                this.updateKpiTableOptions();
            }
        });

        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                panel.style.display = 'none';
            });
        }

        if (runBtn) {
            runBtn.addEventListener('click', () => this.runKpi());
        }
    }

    updateKpiTableOptions() {
        const select = document.getElementById('kpiTableSelect');
        if (!select) return;
        const current = select.value;
        select.innerHTML = '<option value="">Latest detected table</option>';
        this.artifactStore.forEach((artifact, id) => {
            if (artifact.type !== 'table') return;
            const option = document.createElement('option');
            option.value = id;
            option.textContent = `${artifact.title || 'Table'} (${id.slice(0,6)})`;
            select.appendChild(option);
        });
        if (current) {
            select.value = current;
        }
    }

    async runKpi() {
        const panel = document.getElementById('kpiPanel');
        if (!panel) return;
        const metric = document.getElementById('kpiMetric').value.trim();
        const tableId = document.getElementById('kpiTableSelect').value;
        const valueColumn = document.getElementById('kpiValueColumn').value.trim();
        const aggregation = document.getElementById('kpiAggregation').value;
        const dateColumn = document.getElementById('kpiDateColumn').value.trim();
        const dateFrom = document.getElementById('kpiDateFrom').value;
        const dateTo = document.getElementById('kpiDateTo').value;
        const filterInput = document.getElementById('kpiFilters').value.trim();

        const filters = [];
        if (filterInput) {
            filterInput.split(',').forEach(chunk => {
                const [col, val] = chunk.split('=').map(v => v && v.trim());
                if (col && val) {
                    filters.push({ column: col, op: 'eq', value: val });
                }
            });
        }

        const payload = {
            metric,
            table_id: tableId || undefined,
            value_column: valueColumn || undefined,
            aggregation,
            date_column: dateColumn || undefined,
            date_from: dateFrom || undefined,
            date_to: dateTo || undefined,
            filters,
        };

        this.addSystemMessage('Running KPI analysis...');

        try {
            const res = await fetch('/api/kpi/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken(),
                },
                body: JSON.stringify(payload),
            });
            const data = await res.json();
            if (!res.ok || !data.success) {
                throw new Error(data.error || 'Unable to compute KPI');
            }
            this.renderKpiResult(data);
        } catch (err) {
            this.addSystemMessage(`KPI error: ${err.message}`);
        }
    }

    renderKpiResult(result) {
        if (!result || !Array.isArray(result.kpis)) {
            this.addSystemMessage('No KPI results returned.');
            return;
        }
        const esc = (s) => this.escapeHtml(s == null ? '' : s);
        const rows = result.kpis.map(kpi => {
            return `<div class="kpi-row"><div><strong>${esc(kpi.metric)}</strong> (${esc((kpi.aggregation || '').toUpperCase())})</div><div class="kpi-value">${esc(kpi.formatted_value || kpi.value)}</div><div class="kpi-meta">Rows matched: ${kpi.rows_matched || 0}</div></div>`;
        }).join('');
        const summary = esc(result.summary || '');
        const html = `<div class="kpi-result">${rows}<div class="kpi-summary">${summary}</div></div>`;
        this.addRichMessage(html, 'bot');
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
                // Get message and visualizations from response
                const responseMessage = data.message || data.response || '';
                const visualizations = data.visualizations || [];
                
                // Add bot response with typing effect
                this.addMessage(responseMessage, 'bot', true);
                
                // Render visualizations
                if (visualizations && visualizations.length > 0) {
                    console.log(`📊 Rendering ${visualizations.length} visualizations`);
                    visualizations.forEach(viz => {
                        this.renderVisualization(viz);
                    });
                }
                
                // Update status indicator
                this.updateStatusIndicator(data.ai_powered);
                
                // Update conversation ID if provided
                if (data.conversation_id) {
                    this.setConversationId(data.conversation_id);
                }
                
                // Speak the response after typing animation
                setTimeout(() => {
                    console.log('⏰ Timeout triggered for speech');
                    this.speakMessage(responseMessage);
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
        this.messages.push({ content, sender, timestamp: new Date(), type: 'text' });
        this.saveChatHistory();
        
        this.scrollToBottom();
    }
    
    typeMessage(element, text, speed = 30) {
        // Safety check: ensure text exists
        if (!text || typeof text !== 'string') {
            text = String(text || '');
        }
        
        element.innerHTML = '';
        let i = 0;
        
        const typeInterval = setInterval(() => {
            if (text && i < text.length) {
                element.innerHTML += text.charAt(i);
                i++;
                this.scrollToBottom();
            } else {
                clearInterval(typeInterval);
                if (text) {
                    element.innerHTML = this.formatMessage(text);
                }
            }
        }, speed);
    }
    
    formatMessage(message) {
        // Safety check: ensure message is a string
        if (!message || typeof message !== 'string') {
            message = String(message || '');
        }
        
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
            this.addMessageToUI(msg.content, msg.sender, msg.type);
        });
    }

    addMessageToUI(content, sender, type = 'text') {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;

        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'message-avatar';
        avatarDiv.innerHTML = sender === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        if (type === 'html') {
            contentDiv.innerHTML = content;
        } else {
            contentDiv.innerHTML = this.formatMessage(content);
        }

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
