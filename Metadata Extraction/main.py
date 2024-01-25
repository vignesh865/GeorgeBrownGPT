import os
import logging
from functions import extract_info, process_text_file



if __name__ == "__main__":
    folder_path = "programpages2024_files_with_null_values"
    metadata_folder = "metadata_" + folder_path
    os.makedirs(metadata_folder, exist_ok=True)
    log_file_path = os.path.join(metadata_folder, "log_output.txt")
    logging.basicConfig(level=logging.INFO, filename=log_file_path, filemode="a", format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    # Create metadata folder if it doesn't exist
    

    base_url1 = "https://7f09-35-240-188-58.ngrok-free.app"

    txt_files = [filename for filename in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, filename)) and filename.lower().endswith('.txt')]
    total_files_count = len(txt_files)
    processed_files_count = 0  # Initialize counter

    for filename in txt_files:
        file_path = os.path.join(folder_path, filename)

        # Check if the path is a file and has a .txt extension
        if os.path.isfile(file_path) and filename.lower().endswith('.txt'):
            logger.info(f"Processing file: {filename.replace('.txt', '')}")
            process_text_file(file_path, metadata_folder, base_url1)
            processed_files_count += 1  # Increment counter
            remaining_files_count = total_files_count - processed_files_count
            logger.info(f"Remaining files: {remaining_files_count}")
            logger.info('*******************************************************')

    logger.info(f"Total files processed: {processed_files_count}")


    # No need to manually flush and remove the handler, as it's handled by basicConfig
    logging.shutdown() 
