# SEO Audit Tool

A powerful Python-based SEO audit tool that helps you analyze and optimize blog articles for better search engine performance.

## Features

- Article content analysis
- Keyword optimization suggestions
- Internal/external link analysis
- Heading structure review
- Content length assessment
- Manual approval system for changes
- Bulk URL processing
- Local file analysis support

## Installation

1. Clone the repository:
```bash
git clone https://github.com/cm777-dev/seo-audit.git
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install spaCy language model:
```bash
python -m spacy download en_core_web_sm
```

## Usage

Run the Streamlit application:
```bash
streamlit run app.py
```

The application provides three ways to analyze content:
1. Single URL analysis
2. Bulk URL processing
3. Local HTML file analysis

## Analysis Features

- Word count analysis
- Average sentence length calculation
- Heading structure review
- Keyword extraction and analysis
- Internal/external link assessment
- SEO improvement suggestions
- Manual approval system for changes

## Output

Analysis results are saved in the `results` directory in JSON format for future reference.
