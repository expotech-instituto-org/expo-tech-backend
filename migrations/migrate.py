import argparse
import json
import os
from pymongo import MongoClient

def main():
    parser = argparse.ArgumentParser(description="Migrate all JSON documents in the migrations directory to MongoDB.")
    parser.add_argument('--mongo-url', type=str, default='mongodb://localhost:27017', help='MongoDB connection URL (default: mongodb://localhost:27017)')
    parser.add_argument('--db', type=str, default='expotech_db', help='MongoDB database name (default: expo_tech)')
    parser.add_argument('--migrations-dir', type=str, default='./', help='Directory containing JSON files (default: migrations)')
    args = parser.parse_args()

    if not os.path.isdir(args.migrations_dir):
        print(f"Migrations directory not found: {args.migrations_dir}")
        return

    client = MongoClient(args.mongo_url)
    db = client[args.db]

    files = [f for f in os.listdir(args.migrations_dir) if f.endswith('.json')]
    if not files:
        print(f"No JSON files found in {args.migrations_dir}")
        return

    for filename in files:
        path = os.path.join(args.migrations_dir, filename)
        collection_name = os.path.splitext(filename)[0]
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if not isinstance(data, list):
                print(f"Skipping {filename}: JSON data must be a list of objects.")
                continue
            collection = db[collection_name]
            if data:
                result = collection.insert_many(data)
                print(f"Inserted {len(result.inserted_ids)} documents into '{args.db}.{collection_name}'")
            else:
                print(f"No data to insert for {filename}.")
        except Exception as e:
            print(f"Error processing {filename}: {e}")

    client.close()

if __name__ == '__main__':
    main()

