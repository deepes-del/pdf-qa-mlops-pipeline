import json
import logging
from kafka import KafkaConsumer
from datetime import datetime
import os
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EventProcessor:
    def __init__(self):
        self.kafka_config = {
            'bootstrap_servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092'),
            'auto_offset_reset': 'earliest',
            'enable_auto_commit': True,
            'group_id': 'pdf-qa-event-processor',
            'value_deserializer': lambda x: json.loads(x.decode('utf-8'))
        }
        
    def process_pdf_events(self, event: Dict[Any, Any]):
        """Process PDF processing events"""
        event_type = event.get('event_type')
        
        if event_type == 'pdf_processed':
            logger.info(f"PDF processed: {event['pages_count']} pages, {event['text_length']} characters")
        elif event_type == 'pdf_processing_error':
            logger.error(f"PDF processing error: {event['error']}")
            
    def process_embedding_events(self, event: Dict[Any, Any]):
        """Process embedding generation events"""
        event_type = event.get('event_type')
        
        if event_type == 'embeddings_generated':
            logger.info(f"Embeddings generated: {event['chunks_count']} chunks, dimension {event['embedding_dimension']}")
        elif event_type == 'embedding_error':
            logger.error(f"Embedding error: {event['error']}")
            
    def process_query_events(self, event: Dict[Any, Any]):
        """Process query processing events"""
        event_type = event.get('event_type')
        
        if event_type == 'chunks_retrieved':
            logger.info(f"Query processed: retrieved {event['retrieved_chunks']} chunks")
            
    def process_answer_events(self, event: Dict[Any, Any]):
        """Process answer generation events"""
        event_type = event.get('event_type')
        
        if event_type == 'answer_generated':
            logger.info(f"Answer generated: {event['answer_length']} characters")
        elif event_type == 'answer_generation_error':
            logger.error(f"Answer generation error: {event['error']}")

    def start_consumers(self):
        """Start Kafka consumers for different topics"""
        topics = ['pdf_processing', 'embedding_generation', 'query_processing', 'answer_generation']
        
        try:
            consumer = KafkaConsumer(*topics, **self.kafka_config)
            logger.info(f"Started Kafka consumer for topics: {topics}")
            
            for message in consumer:
                try:
                    topic = message.topic
                    event = message.value
                    
                    logger.info(f"Received event from topic {topic}: {event}")
                    
                    if topic == 'pdf_processing':
                        self.process_pdf_events(event)
                    elif topic == 'embedding_generation':
                        self.process_embedding_events(event)
                    elif topic == 'query_processing':
                        self.process_query_events(event)
                    elif topic == 'answer_generation':
                        self.process_answer_events(event)
                        
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    
        except Exception as e:
            logger.error(f"Error starting Kafka consumer: {e}")

if __name__ == "__main__":
    processor = EventProcessor()
    processor.start_consumers()
