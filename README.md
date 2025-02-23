# Brado RAG Demo

View the demo at https://twolven.github.io/brado-rag-demo/

## Overview
This project demonstrates my expertise in Retrieval-Augmented Generation (RAG) by creating a real-time comparison between a base language model (Phi-4) and a RAG-enhanced version. The demo specifically focuses on company-specific knowledge about Brado, showcasing how RAG can significantly improve response accuracy and relevance in a business context.

## Motivation
After discussing RAG implementations during my initial interview, I created this weekend project to demonstrate my practical experience with:
- RAG architecture and implementation
- Vector database integration (Pinecone)
- Real-time streaming responses
- Modern web development practices
- LLM integration and enhancement

## Technical Implementation

### Architecture
- **Frontend**: Single-page application with split-screen interface
- **Backend**: FastAPI server as a relay between frontend and LLMs
- **Vector Database**: Pinecone.io for efficient similarity search
- **Embedding Model**: Nomic Embed Text v1.5
- **Base LLM**: Phi-4

## Security Implementation
To ensure enterprise-grade security and compliance with modern web standards, the project implements:

- End-to-end SSL encryption using Let's Encrypt certificates
- Secure reverse proxy configuration with NGINX
- HTTPS-compliant API endpoints
- GitHub Pages security integration
- Automated certificate management

This security layer ensures safe transmission of queries and responses while maintaining high performance and reliability. The implementation follows industry best practices for protecting data in transit, crucial for enterprise applications handling proprietary information.

### Key Features
- Side-by-side comparison of base vs RAG-enhanced responses
- Real-time response streaming using Server-Sent Events
- Dynamic suggested questions for easy testing
- Responsive design for all devices
- Markdown support in chat interface
- Comprehensive error handling and logging
- ISO/IEC 27001:2013 compliant data handling

### Tech Stack
- **Frontend**:
  - HTML5/CSS3
  - Tailwind CSS
  - Vanilla JavaScript
  - Showdown.js (Markdown conversion)
  
- **Backend**:
  - Python
  - FastAPI
  - Uvicorn
  - Pinecone Python SDK
  - NGINX (Reverse Proxy)
  - Let's Encrypt SSL Certificates
  
- **AI/ML**:
  - Phi-4 Language Model
  - Nomic Embed Text v1.5
  - Custom RAG implementation
  - Pinecone vector database

- **Infrastructure**:
  - GitHub Pages for static hosting
  - Dynamic DNS configuration
  - Windows Server deployment
  - Port forwarding and network security

## Project Structure
```bash
project/
├── index.html         # Main interface
├── app.js            # Frontend logic and API integration
├── README.md         # Project documentation
├── backend/
│   ├── test_rag.py    # FastAPI server implementation
│   ├── rag_serv.py    # RAG server implementation
│   └── test_insert.py # Vector DB population script
```

## RAG Implementation Details

### Vector Database Setup
- Created and populated Pinecone index with company-specific data
- Implemented efficient document chunking and embedding
- Optimized similarity search parameters

### Response Generation
1. Query embedding generation
2. Semantic similarity search in Pinecone
3. Context integration with base prompt
4. Enhanced response generation using Phi-4
5. Real-time streaming to frontend

### Knowledge Base
- Comprehensive company information
- Key personnel and leadership
- Services and methodologies
- Office locations and contact details
- Historical data and milestones

## Future Improvements
- Integration with additional language models
- Enhanced context retrieval algorithms
- User feedback integration
- Response caching for improved performance
- Additional company data integration
- Automated testing suite

## Technical Learning Outcomes
- Implemented production-ready RAG system
- Integrated real-time streaming responses
- Optimized vector similarity search
- Developed clean, maintainable frontend code
- Created scalable backend architecture

## Deployment
The demo is accessible via GitHub Pages. The project showcases the integration of multiple services including LM Studio, Pinecone vector database, and custom FastAPI endpoints for seamless RAG implementation.

## About RAG
Retrieval-Augmented Generation (RAG) enhances language model responses by incorporating relevant external knowledge. This implementation demonstrates how RAG can improve response accuracy and relevance in a business context, particularly for company-specific information where base model knowledge may be limited or outdated.

## Contact
Feel free to reach out with any questions about the implementation or to discuss the technical details further.

---
*This project was developed over a weekend to demonstrate practical RAG implementation skills and showcase real-world applications of AI/ML technologies in a business context.*
