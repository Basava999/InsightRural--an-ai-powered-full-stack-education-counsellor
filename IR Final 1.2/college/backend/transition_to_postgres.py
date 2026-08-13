import os
import shutil
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def transition_to_postgres():
    """
    Cleans up old mock SQLite databases and JSON sample data to enforce the 
    'NO MOCK DATA' critical requirement.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    sqlite_db = os.path.join(base_dir, "insightrural.db")
    
    # 1. Archive old SQLite DB
    if os.path.exists(sqlite_db):
        archive_path = sqlite_db + ".archive"
        shutil.move(sqlite_db, archive_path)
        logging.info(f"Archived old mock SQLite database to {archive_path}")
    else:
        logging.info("No old SQLite database found to archive.")

    # 2. Archive mock JSON data files
    data_dir = os.path.join(os.path.dirname(base_dir), "data")
    if os.path.exists(data_dir):
        archive_dir = os.path.join(data_dir, "mock_archive")
        os.makedirs(archive_dir, exist_ok=True)
        
        for file in os.listdir(data_dir):
            if file.endswith('.json') and 'sample' in file:
                src = os.path.join(data_dir, file)
                dst = os.path.join(archive_dir, file)
                shutil.move(src, dst)
                logging.info(f"Archived mock sample data: {file}")
                
    logging.info("Transition script completed. Ready for Postgres and Data Pipeline execution.")
    logging.warning("Please configure POSTGRES_URL in your environment to point to the new database.")

if __name__ == "__main__":
    transition_to_postgres()
