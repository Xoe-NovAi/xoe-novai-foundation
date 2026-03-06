# GetDBInfo - API Database Information Scraper

A short, efficient program to scrape data from REST API endpoints and extract information for database analysis.

## Features

- 🔍 **Automatic Endpoint Discovery**: Finds available API endpoints automatically
- 📊 **Multiple Output Formats**: JSON and CSV export capabilities
- 🔐 **Authentication Support**: Bearer token authentication
- ⚡ **Async Processing**: High-performance asynchronous requests
- 🛡️ **Error Handling**: Robust error handling and retry logic
- 📈 **Progress Tracking**: Real-time logging and progress updates

## Quick Start

```bash
# Basic usage - scrape all endpoints
python create_api_scraper.py https://api.example.com

# With authentication
python create_api_scraper.py https://api.example.com --auth-token your_token_here

# Save to specific directory
python create_api_scraper.py https://api.example.com --output-dir ./my_data

# Export as CSV only
python create_api_scraper.py https://api.example.com --format csv

# Just discover endpoints (don't scrape data)
python create_api_scraper.py https://api.example.com --discover-only
```

## Installation

```bash
pip install aiohttp pandas
```

## Usage Examples

### Example 1: Basic API Scraping
```bash
python create_api_scraper.py https://jsonplaceholder.typicode.com
```

This will:
1. Discover available endpoints (posts, comments, albums, etc.)
2. Scrape data from each endpoint
3. Save results as JSON and CSV files
4. Create timestamped output files

### Example 2: Enterprise API with Authentication
```bash
python create_api_scraper.py https://api.company.com \
    --auth-token eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9... \
    --output-dir ./company_data \
    --format both
```

### Example 3: Discovery Only
```bash
python create_api_scraper.py https://api.example.com --discover-only
```

Output:
```
users
posts
comments
albums
todos
photos
```

## Output Structure

The scraper creates timestamped output files:

```
scraped_data/
├── api_scrape_20240122_143052.json    # Complete data dump
├── api_scrape_20240122_143052_users.csv
├── api_scrape_20240122_143052_posts.csv
└── api_scrape_20240122_143052_comments.csv
```

## Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `base_url` | Base URL of the API | Required |
| `--auth-token` | Bearer token for authentication | None |
| `--output-dir` | Output directory | `scraped_data` |
| `--format` | Output format (json/csv/both) | `both` |
| `--discover-only` | Only discover endpoints | `false` |

## Endpoint Discovery

The scraper automatically tries common API endpoint patterns:
- `groups`, `participants`, `activities`, `sessions`
- `users`, `data`, `info`, `status`, `metrics`
- Custom endpoints can be added by modifying the `common_endpoints` list

## Error Handling

- **Network Errors**: Automatic retry with exponential backoff
- **Authentication Errors**: Clear error messages for invalid tokens
- **Rate Limiting**: Built-in rate limiting protection
- **Data Format Issues**: Graceful handling of malformed JSON

## Data Export

### JSON Format
Complete data dump with metadata:
```json
{
  "users": [...],
  "posts": [...],
  "users_metadata": {
    "scraped_at": "2024-01-22T14:30:52",
    "endpoint": "users",
    "record_count": 10
  }
}
```

### CSV Format
Clean, analysis-ready CSV files with proper headers and data types.

## Use Cases

- **Database Analysis**: Extract and analyze API data for insights
- **Data Migration**: Export data from APIs for migration projects
- **API Testing**: Verify API responses and data structure
- **Documentation**: Generate examples of API responses
- **Monitoring**: Regular data extraction for trend analysis

## Security Notes

- Bearer tokens are handled securely (not logged)
- HTTPS is enforced for all requests
- No sensitive data is cached or stored
- All temporary data is cleaned up automatically