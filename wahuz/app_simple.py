import streamlit as st
import PyPDF2
import io
import numpy as np
import google.generativeai as genai
import logging
import time
import json
from datetime import datetime
from kafka import KafkaProducer
import os
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MLOpsApp:
    def __init__(self):
        self.kafka_producer = None
        self.setup_kafka()
        
    def setup_kafka(self):
        """Initialize Kafka producer for event streaming"""
        try:
            kafka_config = {
                'bootstrap_servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092'),
                'value_serializer': lambda x: json.dumps(x).encode('utf-8')
            }
            self.kafka_producer = KafkaProducer(**kafka_config)
            logger.info("Kafka producer initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Kafka producer: {e}")
            self.kafka_producer = None

    def send_event(self, topic: str, event_data: Dict[Any, Any]):
        """Send event to Kafka topic"""
        if self.kafka_producer:
            try:
                self.kafka_producer.send(topic, event_data)
                logger.info(f"Event sent to topic {topic}: {event_data}")
            except Exception as e:
                logger.error(f"Failed to send event to Kafka: {e}")

    def extract_text_from_pdf(self, file_bytes: bytes) -> str:
        """Extract text from PDF with monitoring"""
        try:
            reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            
            # Send event to Kafka
            self.send_event('pdf_processing', {
                'timestamp': datetime.now().isoformat(),
                'event_type': 'pdf_processed',
                'pages_count': len(reader.pages),
                'text_length': len(text)
            })
            
            logger.info(f"PDF processed successfully: {len(reader.pages)} pages, {len(text)} characters")
            return text
        except Exception as e:
            logger.error(f"Error processing PDF: {e}")
            self.send_event('pdf_processing', {
                'timestamp': datetime.now().isoformat(),
                'event_type': 'pdf_processing_error',
                'error': str(e)
            })
            raise

    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into chunks"""
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunks.append(text[start:end])
            start = end - overlap
        
        logger.info(f"Text chunked into {len(chunks)} pieces")
        return chunks

    def build_index(self, chunks: List[str]) -> np.ndarray:
        """Build embeddings index with monitoring"""
        try:
            embeddings = []
            embed_model = "models/text-embedding-004"
            
            for i, chunk in enumerate(chunks):
                emb = genai.embed_content(model=embed_model, content=chunk)["embedding"]
                embeddings.append(emb)
                
                if i % 10 == 0:  # Log progress every 10 chunks
                    logger.info(f"Generated embeddings for {i+1}/{len(chunks)} chunks")
            
            embeddings = np.array(embeddings)
            embeddings = embeddings / (np.linalg.norm(embeddings, axis=1, keepdims=True) + 1e-12)
            
            # Send event to Kafka
            self.send_event('embedding_generation', {
                'timestamp': datetime.now().isoformat(),
                'event_type': 'embeddings_generated',
                'chunks_count': len(chunks),
                'embedding_dimension': embeddings.shape[1]
            })
            
            logger.info(f"Index built successfully: {embeddings.shape}")
            return embeddings
        except Exception as e:
            logger.error(f"Error building index: {e}")
            self.send_event('embedding_generation', {
                'timestamp': datetime.now().isoformat(),
                'event_type': 'embedding_error',
                'error': str(e)
            })
            raise

    def retrieve(self, query: str, chunks: List[str], embeddings: np.ndarray, top_k: int = 3) -> List[str]:
        """Retrieve relevant chunks"""
        try:
            embed_model = "models/text-embedding-004"
            q_emb = genai.embed_content(model=embed_model, content=query)["embedding"]
            q_emb = np.array(q_emb) / (np.linalg.norm(q_emb) + 1e-12)
            scores = np.dot(embeddings, q_emb)
            top_idx = np.argsort(-scores)[:top_k]
            
            retrieved_chunks = [chunks[i] for i in top_idx]
            
            # Send event to Kafka
            self.send_event('query_processing', {
                'timestamp': datetime.now().isoformat(),
                'event_type': 'chunks_retrieved',
                'query_length': len(query),
                'retrieved_chunks': len(retrieved_chunks),
                'top_scores': scores[top_idx].tolist()
            })
            
            return retrieved_chunks
        except Exception as e:
            logger.error(f"Error retrieving chunks: {e}")
            raise

    def ask_gemini(self, context: str, question: str) -> str:
        """Generate answer using Gemini"""
        try:
            prompt = f"Answer the question using only the following context. If not found, say you don't know.\n\nContext:\n{context}\n\nQuestion: {question}"
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            
            # Send event to Kafka
            self.send_event('answer_generation', {
                'timestamp': datetime.now().isoformat(),
                'event_type': 'answer_generated',
                'question_length': len(question),
                'context_length': len(context),
                'answer_length': len(response.text)
            })
            
            return response.text
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            self.send_event('answer_generation', {
                'timestamp': datetime.now().isoformat(),
                'event_type': 'answer_generation_error',
                'error': str(e)
            })
            raise

def main():
    app = MLOpsApp()
    
    st.title("PDF Q&A with Gemini - MLOps Edition")
    st.sidebar.info("🔧 MLOps Features: Kafka Events, Structured Logging")

    # API Key input
    gemini_api_key = st.text_input("Enter your Google Gemini API Key", type="password")
    if gemini_api_key:
        genai.configure(api_key=gemini_api_key)
    else:
        st.warning("Please enter your Gemini API key to continue.")
        return

    # File upload
    uploaded = st.file_uploader("Upload a PDF", type=["pdf"])
    
    if uploaded is not None and gemini_api_key:
        with st.spinner("Processing PDF..."):
            try:
                pdf_bytes = uploaded.read()
                text = app.extract_text_from_pdf(pdf_bytes)
                chunks = app.chunk_text(text)
                embeddings = app.build_index(chunks)
                
                st.success("PDF processed successfully!")
                st.info(f"📄 Processed {len(chunks)} text chunks")
                
                # Store in session state
                st.session_state['chunks'] = chunks
                st.session_state['embeddings'] = embeddings
                
            except Exception as e:
                st.error(f"Error processing PDF: {e}")
                logger.error(f"PDF processing failed: {e}")

    # Q&A Interface
    if 'chunks' in st.session_state and 'embeddings' in st.session_state:
        question = st.text_input("Ask a question about the PDF")
        
        if st.button("Get Answer"):
            if question.strip():
                try:
                    with st.spinner("Generating answer..."):
                        top_chunks = app.retrieve(
                            question, 
                            st.session_state['chunks'], 
                            st.session_state['embeddings']
                        )
                        context = "\n\n".join(top_chunks)
                        answer = app.ask_gemini(context, question)
                        
                        st.subheader("Answer")
                        st.write(answer)
                        
                        with st.expander("Retrieved Context"):
                            st.write(context)
                            
                        with st.expander("Debug Info"):
                            st.json({
                                "question_length": len(question),
                                "context_length": len(context),
                                "chunks_retrieved": len(top_chunks),
                                "timestamp": datetime.now().isoformat()
                            })
                            
                except Exception as e:
                    st.error(f"Error generating answer: {e}")
                    logger.error(f"Answer generation failed: {e}")
            else:
                st.warning("Please enter a question.")

    # Status display
    with st.sidebar:
        st.subheader("📊 System Status")
        st.success("✅ Kafka Events Active")
        st.success("✅ Logging Active")
        if 'chunks' in st.session_state:
            st.info(f"📄 {len(st.session_state['chunks'])} chunks loaded")

if __name__ == "__main__":
    main()
