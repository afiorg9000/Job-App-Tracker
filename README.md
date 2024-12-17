# Job Application Tracker

A Python script that automatically extracts job posting information and saves it to a Notion database. Uses GPT-3.5 to analyze job descriptions and extract relevant details.

## Features

- Extract job information from URLs
- Process single URLs or batch process from a text file
- Automatically detects:
  - Job title
  - Company name
  - Location
  - Tech stack requirements
- Saves all information to a Notion database
- Provides detailed processing summaries and error reporting

## Prerequisites

- Python 3.6+
- Notion API key
- OpenAI API key
- Notion database ID

## Installation

1. Clone the repository
2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root with:
```env
NOTION_API_KEY=your_notion_api_key
NOTION_DATABASE_ID=your_database_id
OPENAI_API_KEY=your_openai_api_key
```

## Usage

Run the script:
```bash
python job_tracker.py
```

You'll be prompted to choose between:
1. Process a single URL
2. Process multiple URLs from jobs.txt

### Single URL Mode
Enter the job posting URL when prompted.

### Batch Processing Mode
Create a jobs.txt file with one URL per line, then select option 2.

## Notion Database Setup

Your Notion database should have the following properties:
- Title (title)
- Company (rich text)
- Location (rich text)
- Tech Stack (rich text)
- Status (select)
- URL (url)
- Date Added (date)
- Source (select)

## Error Handling

The script includes comprehensive error handling for:
- Invalid URLs
- Network issues
- File reading errors
- API failures

Failed URLs are logged with specific error messages in the processing summary.

## Dependencies

```python:requirements.txt
startLine: 1
endLine: 4
```

## License

MIT License

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request
