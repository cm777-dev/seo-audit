import streamlit as st
import pandas as pd
import nltk
from bs4 import BeautifulSoup
import requests
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from pathlib import Path
import json
import re
from datetime import datetime

# Download required NLTK data
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')

class SEOAuditor:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.results_dir = Path("results")
        self.results_dir.mkdir(exist_ok=True)
        
    def analyze_article(self, url):
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract text content
            text = ' '.join([p.text for p in soup.find_all('p')])
            
            # Basic SEO metrics
            word_count = len(text.split())
            sentences = nltk.sent_tokenize(text)
            avg_sentence_length = word_count / len(sentences) if sentences else 0
            
            # Extract headings
            headings = []
            for i in range(1, 7):
                headings.extend([h.text.strip() for h in soup.find_all(f'h{i}')])
            
            # Extract links
            internal_links = []
            external_links = []
            domain = re.findall(r'https?://(?:www\.)?([^/]+)', url)[0]
            
            for a in soup.find_all('a', href=True):
                link = {'text': a.text.strip(), 'href': a.get('href')}
                if domain in link['href']:
                    internal_links.append(link)
                else:
                    external_links.append(link)
            
            # Analyze keywords using spaCy
            doc = self.nlp(text)
            keywords = {}
            for token in doc:
                if not token.is_stop and token.is_alpha and len(token.text) > 2:
                    keywords[token.text.lower()] = keywords.get(token.text.lower(), 0) + 1
            
            # Sort keywords by frequency
            sorted_keywords = dict(sorted(keywords.items(), key=lambda x: x[1], reverse=True)[:10])
            
            return {
                'url': url,
                'analyzed_at': datetime.now().isoformat(),
                'metrics': {
                    'word_count': word_count,
                    'avg_sentence_length': avg_sentence_length,
                    'num_headings': len(headings),
                    'num_internal_links': len(internal_links),
                    'num_external_links': len(external_links)
                },
                'headings': headings,
                'internal_links': internal_links,
                'external_links': external_links,
                'top_keywords': sorted_keywords
            }
        except Exception as e:
            return {'error': str(e)}

    def suggest_improvements(self, analysis):
        suggestions = []
        metrics = analysis['metrics']
        
        # Word count check
        if metrics['word_count'] < 300:
            suggestions.append({
                'category': 'Content Length',
                'issue': 'Content is too short',
                'suggestion': 'Aim for at least 300 words for better SEO performance.',
                'priority': 'High'
            })
        
        # Sentence length check
        if metrics['avg_sentence_length'] > 20:
            suggestions.append({
                'category': 'Readability',
                'issue': 'Sentences are too long',
                'suggestion': 'Try to keep average sentence length under 20 words for better readability.',
                'priority': 'Medium'
            })
        
        # Heading check
        if metrics['num_headings'] == 0:
            suggestions.append({
                'category': 'Structure',
                'issue': 'No headings found',
                'suggestion': 'Add hierarchical headings (H1, H2, etc.) to improve content structure.',
                'priority': 'High'
            })
        
        # Link check
        if metrics['num_internal_links'] < 2:
            suggestions.append({
                'category': 'Internal Linking',
                'issue': 'Few internal links',
                'suggestion': 'Add more internal links to improve site structure and SEO.',
                'priority': 'Medium'
            })
        
        if metrics['num_external_links'] == 0:
            suggestions.append({
                'category': 'External Linking',
                'issue': 'No external links',
                'suggestion': 'Consider adding relevant external links to authoritative sources.',
                'priority': 'Low'
            })
        
        return suggestions

    def save_analysis(self, analysis, approved=False):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = re.sub(r'[^\w\-_.]', '_', analysis['url'])
        status = 'approved' if approved else 'pending'
        output_file = self.results_dir / f"{filename}_{status}_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        
        return output_file

def main():
    st.set_page_config(page_title="SEO Audit Tool", layout="wide")
    st.title("SEO Audit Tool")
    
    # Initialize SEO Auditor
    auditor = SEOAuditor()
    
    # Input methods
    input_method = st.radio(
        "Choose input method:",
        ("Single URL", "Bulk URLs", "Local Files")
    )
    
    if input_method == "Single URL":
        url = st.text_input("Enter URL to analyze:")
        if url and st.button("Analyze"):
            with st.spinner("Analyzing..."):
                analysis = auditor.analyze_article(url)
                if 'error' in analysis:
                    st.error(f"Error: {analysis['error']}")
                else:
                    display_analysis(analysis, auditor)
    
    elif input_method == "Bulk URLs":
        urls = st.text_area("Enter URLs (one per line):")
        if urls and st.button("Analyze All"):
            urls_list = urls.split('\n')
            for url in urls_list:
                if url.strip():
                    with st.spinner(f"Analyzing {url}..."):
                        analysis = auditor.analyze_article(url.strip())
                        if 'error' in analysis:
                            st.error(f"Error analyzing {url}: {analysis['error']}")
                        else:
                            display_analysis(analysis, auditor)
                            st.markdown("---")
    
    elif input_method == "Local Files":
        st.warning("Feature coming soon: Local file analysis")

def display_analysis(analysis, auditor):
    st.subheader(f"Analysis for: {analysis['url']}")
    
    # Display metrics
    metrics = analysis['metrics']
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Word Count", metrics['word_count'])
    with col2:
        st.metric("Avg Sentence Length", f"{metrics['avg_sentence_length']:.1f}")
    with col3:
        st.metric("Number of Headings", metrics['num_headings'])
    
    # Display headings
    if analysis['headings']:
        st.subheader("Headings")
        for heading in analysis['headings']:
            st.write(f"- {heading}")
    
    # Display keywords
    st.subheader("Top Keywords")
    keywords_df = pd.DataFrame(
        list(analysis['top_keywords'].items()),
        columns=['Keyword', 'Frequency']
    )
    st.dataframe(keywords_df)
    
    # Display links
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(f"Internal Links ({len(analysis['internal_links'])})")
        for link in analysis['internal_links']:
            st.write(f"- [{link['text']}]({link['href']})")
    with col2:
        st.subheader(f"External Links ({len(analysis['external_links'])})")
        for link in analysis['external_links']:
            st.write(f"- [{link['text']}]({link['href']})")
    
    # Display suggestions
    st.subheader("Improvement Suggestions")
    suggestions = auditor.suggest_improvements(analysis)
    for suggestion in suggestions:
        with st.expander(f"{suggestion['category']}: {suggestion['issue']} (Priority: {suggestion['priority']})"):
            st.write(suggestion['suggestion'])
    
    # Save options
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Save Analysis"):
            file_path = auditor.save_analysis(analysis)
            st.success(f"Analysis saved to {file_path}")
    with col2:
        if st.button("Approve and Save"):
            file_path = auditor.save_analysis(analysis, approved=True)
            st.success(f"Analysis approved and saved to {file_path}")

if __name__ == "__main__":
    main()
