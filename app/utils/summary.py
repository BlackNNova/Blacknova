import re
import logging
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from transformers import pipeline
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set NLTK data path and download required resources
nltk_data_path = '/home/ubuntu/nltk_data'
os.makedirs(nltk_data_path, exist_ok=True)
nltk.data.path.insert(0, nltk_data_path)

# Download required NLTK data
try:
    nltk.download('punkt', download_dir=nltk_data_path)
    nltk.download('stopwords', download_dir=nltk_data_path)
except Exception as e:
    logger.error(f"Error downloading NLTK data: {str(e)}")

def clean_text(text):
    """Clean and normalize text for processing"""
    # Remove special characters and extra whitespace
    text = re.sub(r'[^\w\s.]', ' ', text)
    text = ' '.join(text.split())
    return text

def simple_sentence_split(text):
    """Simple sentence tokenization fallback"""
    # Split on periods followed by whitespace or end of string
    sentences = re.split(r'\.(?:\s+|\s*$)', text)
    # Remove empty strings and clean up
    sentences = [s.strip() for s in sentences if s.strip()]
    # Add periods back
    sentences = [s + '.' for s in sentences]
    return sentences

def identify_subtle_points(text):
    """Identify subtle but critical points in the text"""
    try:
        # Clean and tokenize text
        cleaned_text = clean_text(text)
        try:
            sentences = sent_tokenize(cleaned_text)
        except Exception:
            logger.warning("NLTK tokenization failed, using simple split")
            sentences = simple_sentence_split(cleaned_text)

        # Keywords that might indicate subtle requirements
        subtle_keywords = [
            'required', 'must', 'essential', 'critical', 'attention',
            'special', 'specific', 'important', 'crucial', 'necessary',
            'deadline', 'format', 'follow', 'include', 'consider'
        ]

        # Find sentences containing subtle points
        subtle_points = []
        for sentence in sentences:
            words = sentence.lower().split()  # Simple word tokenization
            if any(keyword in words for keyword in subtle_keywords):
                subtle_points.append(sentence.strip())

        # Return top 3 most relevant subtle points
        return subtle_points[:3] if subtle_points else None

    except Exception as e:
        logger.error(f"Error in identify_subtle_points: {str(e)}")
        return None

def generate_order_summary(description, files=None):
    """Generate a summary of the order description and identify subtle points"""
    try:
        logger.info("Initializing summarizer...")
        summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

        logger.info("Generating summary...")
        # Clean and prepare text
        text = clean_text(description)

        # Process files if provided
        if files:
            logger.info(f"Processing {len(files)} files...")
            for file in files:
                try:
                    content = file.read().decode('utf-8')
                    # Add file content to text with a separator
                    text += "\n\nFile Content:\n" + clean_text(content)
                except Exception as e:
                    logger.error(f"Error reading file {file.filename}: {str(e)}")
                finally:
                    file.seek(0)  # Reset file pointer for potential future reads

        # Generate initial summary
        summary_output = summarizer(text, max_length=130, min_length=30,
                                  do_sample=False)[0]['summary_text']

        # Ensure summary is no more than 5 sentences
        try:
            summary_sentences = sent_tokenize(summary_output)
        except Exception:
            logger.warning("NLTK tokenization failed, using simple split")
            summary_sentences = simple_sentence_split(summary_output)

        if len(summary_sentences) > 5:
            summary_output = ' '.join(summary_sentences[:5])

        # Identify subtle points
        subtle_points = identify_subtle_points(text)

        # Format the response
        response = {
            'summary': summary_output,
            'subtle_points': subtle_points
        }

        return response

    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}")
        return {'summary': None, 'subtle_points': None}
