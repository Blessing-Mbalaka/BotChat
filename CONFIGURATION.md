# 🔧 Configuration Guide for HealthBot AI

## Setting up Gemini API

### Step 1: Get Your API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated API key

### Step 2: Configure Environment
Edit the `.env` file in your project root:

```env
# Replace this with your actual API key
GEMINI_API_KEY=AIzaSyD...your_actual_key_here

# Keep these for development
DEBUG=True
SECRET_KEY=your_secret_key_here
```

### Step 3: Test the Configuration
1. Start the server: `python manage.py runserver`
2. Open http://127.0.0.1:8000/
3. Try asking a health question
4. You should see intelligent responses from Gemini AI

## Adding Medical Documents

### Supported Formats
- **PDF files**: Medical journals, research papers
- **Word documents**: Health guides, protocols
- **Text files**: FAQ documents, symptom lists
- **Markdown files**: Formatted health information

### Document Organization
```
medical_docs/
├── symptoms/
│   ├── common_symptoms.md
│   └── emergency_symptoms.pdf
├── medications/
│   ├── otc_medications.docx
│   └── drug_interactions.txt
└── wellness/
    ├── nutrition_guide.pdf
    └── exercise_recommendations.md
```

### Processing Notes
- Documents are automatically indexed when the server starts
- Large documents are chunked for better search
- Content is filtered for medical relevance
- Processing happens in the background

## Customizing Medical Sources

Edit `medical_sources.yaml` to configure web search:

```yaml
medical_sources:
  primary_sites:
    - name: "Mayo Clinic"
      url: "https://www.mayoclinic.org"
      search_endpoint: "/search"
      priority: 1
      categories: ["symptoms", "diseases", "treatments"]
    
    - name: "Your Custom Medical Site"
      url: "https://example-medical-site.com"
      priority: 2
      categories: ["specialized-conditions"]

  search_parameters:
    max_results: 5
    timeout: 10
    headers:
      User-Agent: "HealthBot/1.0"

rag_settings:
  local_docs_path: "./medical_docs"
  chunk_size: 1000
  overlap: 200
  similarity_threshold: 0.7
  max_context_length: 4000
```

## Performance Tuning

### For Better Response Times
```yaml
# In medical_sources.yaml
rag_settings:
  chunk_size: 500          # Smaller chunks = faster search
  similarity_threshold: 0.8 # Higher threshold = fewer results
  max_context_length: 2000  # Less context = faster generation
```

### For Better Quality
```yaml
# In medical_sources.yaml  
rag_settings:
  chunk_size: 1500          # Larger chunks = more context
  similarity_threshold: 0.5 # Lower threshold = more results
  max_context_length: 6000  # More context = better responses
```

## Security Considerations

### API Key Security
- Never commit your actual API key to version control
- Use environment variables for all sensitive data
- Consider using key rotation for production
- Monitor API usage and set usage limits

### Content Safety
- The system includes automatic medical disclaimers
- Responses encourage professional consultation
- Emergency situations are clearly identified
- No personal health data is stored

### Production Deployment
```env
# Production settings
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
SECRET_KEY=your-strong-secret-key-here
GEMINI_API_KEY=your-production-api-key
```

## Troubleshooting

### Common Issues

**"Module not found" errors:**
```bash
# Ensure virtual environment is activated
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Reinstall packages
pip install -r requirements.txt
```

**"API key not found" errors:**
- Check `.env` file exists and contains your key
- Verify the key starts with "AIzaSy"
- Ensure no extra spaces around the key

**"No module named 'dotenv'" errors:**
```bash
pip install python-dotenv
```

**Slow response times:**
- Reduce `max_context_length` in configuration
- Increase `similarity_threshold` to return fewer results
- Consider upgrading to a faster Gemini model

### Debug Mode

Enable verbose logging by setting:
```env
DEBUG=True
DJANGO_LOG_LEVEL=DEBUG
```

Then check the console output for detailed information about:
- Document processing
- API calls to Gemini
- Search operations
- Error details

## Advanced Features

### Custom Health Responses
You can extend the simple response system in `views.py`:

```python
responses = {
    'your_keyword': """
    **Your Custom Health Topic:**
    
    Your detailed health information here...
    
    **When to seek care:**
    • Specific warning signs
    • Emergency indicators
    
    **Home care:**
    • Self-care recommendations
    • Prevention tips
    """
}
```

### Adding New Medical Sites
Extend the web search functionality:

```python
# In web_search_service.py
def get_custom_site_simulation(self, query):
    return [{
        'title': f'Custom Site: {query.title()}',
        'url': 'https://your-medical-site.com',
        'snippet': f'Information about {query} from trusted source.',
        'source': 'Your Medical Site'
    }]
```

### Custom Styling
Modify `chatbot.css` to match your brand:

```css
:root {
    --primary-color: #your-brand-color;
    --secondary-color: #your-accent-color;
    /* ... other custom colors */
}
```

## Getting Help

### Documentation
- README.md - Complete setup guide
- Code comments - Inline documentation
- Django docs - https://docs.djangoproject.com/

### Support Channels
- GitHub Issues - Bug reports and feature requests
- Django Community - General Django questions
- Google AI Studio - Gemini API support

### Contributing
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

---

🏥 **HealthBot AI - Making health information more accessible through AI**