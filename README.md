# FaspAPI Application

## Prerequisites

- Python 3.8+
- pip
- (Optional) Virtual environment

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd expo-tech-backend
```

2. (Optional) Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the Application

Start the FastAPI server:

```bash
docker-compose -f docker-compose-local.yml up -d --build
uvicorn app.main:app --reload
```

- The API will be available at `http://127.0.0.1:8000`
- Interactive docs: `http://127.0.0.1:8000/docs`

## Environment Variables

Configure any required environment variables in a `.env` file.

## Testing

Run tests with:

```bash
pytest
```

## Database Migration

To import JSON data into MongoDB, use the migration script:

```bash
python migrations/migrate.py --mongo-url <MONGO_URL> --db <DB_NAME> --migrations-dir <PATH_TO_JSON_FILES>
```

- `--mongo-url`: MongoDB connection URL (default: `mongodb://localhost:27017`)
- `--db`: Database name (default: `expotech_db`)
- `--migrations-dir`: Directory containing JSON files (default: `./`)

Each JSON file should contain a list of objects. The script will create a collection for each file (using the filename as the collection name) and insert the data.

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Uvicorn Documentation](https://www.uvicorn.org/)
- [Python Documentation](https://docs.python.org/3/)
