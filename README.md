# 🏥 Healthcare AI Chatbot - Your Personal Health Assistant

A sophisticated AI-powered healthcare chatbot built with Django and Google's Gemini AI, designed to provide reliable medical information with voice capabilities and real-time web search integration from trusted medical sources.

## ✨ Features

### 🎨 Modern UI/UX
- **Health-themed Bootstrap design** with professional medical color palette
- **Animated thinking indicators** with pulsing heartbeat effects
- **Responsive design** that works on desktop, tablet, and mobile
- **Professional animations** including slide-in messages, rotating avatars, and smooth transitions
- **Accessibility features** with proper ARIA labels and keyboard navigation

### 🤖 AI-Powered Chatbot
- **Gemini API 2.5 Flash integration** for intelligent responses
- **Context-aware conversations** with conversation history
- **Medical knowledge base** with RAG for enhanced responses
- **Web search integration** for up-to-date medical information
- **Safety-first approach** with medical disclaimers and professional advice recommendations

### 📚 Knowledge Management
- **Local document processing** (PDF, DOCX, TXT, MD) for medical references
- **Intelligent chunking** and similarity search for relevant context
- **Medical site integration** (Mayo Clinic, WebMD, Healthline, MedlinePlus)
- **Configurable search parameters** via YAML configuration

### 🛡️ Safety & Compliance
- **Medical disclaimers** on all responses
- **Professional consultation reminders** for serious symptoms
- **Content filtering** for medical relevance
- **Emergency situation guidance** with clear escalation paths

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ 
- Virtual environment (recommended)
- Gemini API key (for AI responses)

### Installation

1. **Clone and setup the project:**
```bash
cd E:\Healthcare_Bot
python -m venv .venv
.\.venv\Scripts\activate  # On Windows
```

2. **Install dependencies:**
```bash
pip install django python-dotenv google-generativeai requests beautifulsoup4 pyyaml numpy python-docx PyPDF2
```

3. **Configure environment variables:**
Create/edit `.env` file:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
DEBUG=True
```

4. **Run database migrations:**
```bash
python manage.py migrate
```

5. **Start the development server:**
```bash
python manage.py runserver
```

6. **Access the chatbot:**
Open your browser and go to: `http://127.0.0.1:8000/`

## 🎯 Usage Guide

### Basic Chat Features
- **Type your health questions** in the input field
- **Use quick action buttons** for common health topics:
  - 🌡️ Check Symptoms
  - 💊 Medication Info  
  - 🌿 Wellness Tips
  - 🚑 Emergency Info
- **Click suggestion chips** for example queries
- **Clear chat history** with the clear button
- **Export conversations** for your records

### Sample Queries
Try asking about:
- "What are the symptoms of flu?"
- "How to lower blood pressure naturally?"
- "What foods boost immune system?"
- "When should I see a doctor for headaches?"
- "What's the difference between acetaminophen and ibuprofen?"

### Medical Document Integration
Place your medical documents in the `medical_docs/` folder:
- **Supported formats**: PDF, DOCX, TXT, MD
- **Automatic processing**: Documents are automatically indexed
- **Context integration**: Relevant information is included in AI responses

## ⚙️ Configuration

### Medical Sources Configuration (`medical_sources.yaml`)
```yaml
medical_sources:
  primary_sites:
    - name: "Mayo Clinic"
      url: "https://www.mayoclinic.org"
      priority: 1
      categories: ["symptoms", "diseases", "treatments"]
    # Add more medical sites...

rag_settings:
  local_docs_path: "./medical_docs"
  chunk_size: 1000
  similarity_threshold: 0.7
```

### Environment Variables (`.env`)
```env
# Required for AI responses
GEMINI_API_KEY=your_api_key_here

# Optional settings
DEBUG=True
SECRET_KEY=your_secret_key_here
```

## 🎨 Customization

### Color Palette
The health theme uses a professional medical color scheme:
- **Primary Blue**: `#2c7be5` (Trust, reliability)
- **Medical Green**: `#34a853` (Health, wellness)  
- **Warning Orange**: `#fd7e14` (Caution, attention)
- **Danger Red**: `#e63757` (Emergency, critical)

### Animations
- **Heartbeat pulse** on the logo (2s infinite)
- **Typing indicators** with bouncing dots
- **Slide-in messages** with smooth transitions
- **Hover effects** on interactive elements
- **Loading spinners** during AI processing

### Responsive Design
- **Desktop**: Full sidebar with quick actions
- **Tablet**: Collapsible sidebar with swipe gestures  
- **Mobile**: Hidden sidebar with hamburger menu

## 🔧 Advanced Features

### RAG (Retrieval-Augmented Generation)
The system processes local medical documents to enhance AI responses:
1. **Document chunking** with configurable sizes
2. **Similarity search** using embeddings
3. **Context injection** into AI prompts
4. **Relevance filtering** for medical content

### Web Search Integration
Configured to search trusted medical sources:
- **Rate limiting** to respect site policies
- **Content filtering** for medical relevance
- **Source attribution** in responses
- **Configurable priority** for different sites

### Conversation Management
- **Session tracking** with unique conversation IDs
- **Message history** stored locally
- **Context preservation** across chat sessions
- **Export functionality** for chat records

## 🛡️ Safety & Disclaimers

### Medical Disclaimers
Every AI response includes appropriate medical disclaimers:
- Emphasizes educational purpose only
- Recommends professional consultation
- Highlights emergency situations
- Provides clear escalation guidance

### Content Safety
- **Medical keyword filtering** ensures health-related responses
- **Professional language** maintains medical appropriateness  
- **Emergency detection** provides immediate care guidance
- **Liability protection** through clear disclaimers

## 📱 Mobile Experience

### Touch-Friendly Interface
- **Large touch targets** for easy interaction
- **Swipe gestures** for navigation
- **Responsive typography** for readability
- **Optimized animations** for mobile performance

### Progressive Web App Features
- **Offline capability** for basic functionality
- **Install prompts** for home screen access
- **Push notifications** for health reminders (future)
- **Background sync** for message delivery (future)

## 🔮 Future Enhancements

### Planned Features
- **Voice input/output** for hands-free interaction
- **Symptom checker** with decision tree logic
- **Medication reminders** with scheduling
- **Health tracking** integration with wearables
- **Telemedicine integration** for professional consultations
- **Multi-language support** for global accessibility

### AI Improvements
- **Fine-tuned medical models** for specialized responses
- **Image analysis** for visual symptom assessment
- **Predictive health insights** based on conversation patterns
- **Personalized recommendations** using user history

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Important Disclaimers

### Medical Disclaimer
This application provides general health information only and is not intended to:
- Replace professional medical advice, diagnosis, or treatment
- Provide specific medical recommendations
- Diagnose medical conditions
- Prescribe medications or treatments

**Always consult qualified healthcare professionals for medical concerns.**

### Emergency Situations
For medical emergencies:
- **Call 911** (US) or your local emergency number
- **Go to the nearest emergency room**
- **Contact your healthcare provider immediately**

This application is not designed for emergency medical situations.

### Data Privacy
- Conversations may be logged for improvement purposes
- No personal health information should be shared
- Use generic terms when describing symptoms
- Export and delete conversation data as needed

## 📞 Support

For technical support or questions:
- Create an issue on GitHub
- Check the documentation wiki
- Review the FAQ section
- Contact the development team

---

**Built with ❤️ for better health communication and education.**