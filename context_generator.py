import os
import time
from pathlib import Path

import pandas as pd
from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document
from langchain.prompts import PromptTemplate
from langchain.text_splitter import TokenTextSplitter
from langchain_community.llms import Ollama
from tqdm.auto import tqdm

CHUNK_SIZE = 512
MODEL_NAME = "mistral"
BASE_URL = "https://af08-104-196-109-243.ngrok-free.app"


def read_data(path):
    data = None

    with open(path, "r") as fp:
        data = fp.read()

    return data


def split_to_chunks(data):
    text_splitter = TokenTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=20)
    chunked_docs = text_splitter.split_text(data)
    print("Total Chunked docs - ", len(chunked_docs))

    return chunked_docs


def clean_chunks(chunked_docs):
    llm = Ollama(
        base_url=BASE_URL,
        model=MODEL_NAME
    )

    summary_template = """
    You are an expert in extracting information from the scraped webpage contents of the college.
    Your goal is to extract a key information content from the below text.
    
    --------
    {text}
    --------
    
    If there is no key information in the text related to program offered by the college, YOU MUST return the empty text.
    Include all FACTUAL information and entities such as years, numbers, emails, names, etc if available.
    
    EXTRACTED INFORMATION:
    """;

    summary_prompt = PromptTemplate.from_template(summary_template)

    summary_chain = load_summarize_chain(llm, chain_type="stuff",
                                         prompt=summary_prompt
                                         )

    contexts = []

    error_context = []
    for i, doc in tqdm(enumerate(chunked_docs)):

        print(f"Processing #{i} doc")
        try:
            final_summary = summary_chain({"input_documents": [Document(page_content=doc)]}, return_only_outputs=True)
            contexts.append(final_summary.get("output_text"))
        except Exception as ex:
            error_context.append(doc)
            print(f"Error #{i} doc {ex}")
            continue

        print(f"Completed #{i} doc")

    return contexts


def get_files(start_path):
    paths = []
    for root, dirs, files in os.walk(start_path):
        for file in files:
            if file != ".DS_Store":
                paths.append(os.path.join(root, file))

    return paths


def exclude_invalid_creations(contexts_list, invalid_creations):
    # Create sets after replacing starting paths
    set1_replaced = set(contexts_list)
    set2_replaced = set(invalid_creations)

    # Find files unique to each list after replacing starting paths
    return set1_replaced - set2_replaced


def exclude_valid_creations(scraped_pages_list, contexts_list):
    # Replace the starting paths
    # list1_replaced = [os.path.splitext(file)[0] for file in scraped_pages_list]
    list2_replaced = [os.path.splitext(file.replace("contexts", "scraped_pages", 1))[0] + ".txt" for file in
                      contexts_list]

    # Create sets after replacing starting paths
    set1_replaced = set(scraped_pages_list)
    set2_replaced = set(list2_replaced)

    # Find files unique to each list after replacing starting paths
    return set1_replaced - set2_replaced


def get_empty_dfs(context_paths):
    return [path for path in context_paths if pd.read_csv(path).shape[0] == 0]


def print_invalid_creations(context_paths):
    scraped_paths = [os.path.splitext(path.replace("contexts", "scraped_pages", 1))[0] + ".txt" for path in
                     context_paths]
    for path in scraped_paths:
        print("Data: ", read_data(path))


def main():
    files_list = get_files("scraped_pages")
    already_created = get_files("contexts")
    invalid_creations = get_empty_dfs(already_created)
    print_invalid_creations(invalid_creations)

    valid_creations = exclude_invalid_creations(already_created, invalid_creations)
    paths = exclude_valid_creations(files_list, valid_creations)

    print("Total files - ", len(files_list))
    print("Already created files - ", len(already_created))
    print("Invalid creations - ", len(invalid_creations))

    print("Remaining files - ", len(paths))

    for path_id, path in enumerate(paths):
        print(f"Starting #{path_id}- ", path)

        filepath, file_extension = os.path.splitext(path)
        filename = filepath.split("/")[-1]

        new_path = "/".join(filepath.split("/")[:-1]).replace("scraped_pages", "contexts")
        Path(new_path).mkdir(parents=True, exist_ok=True)

        data = read_data(path)
        chunked_docs = split_to_chunks(data)
        contexts = clean_chunks(chunked_docs)

        if len(contexts) == 0:
            print("No context present")
            continue

        ids = [str(time.time_ns()) for _ in contexts]
        df = pd.DataFrame({"Id": ids, "Context": contexts, "file_path": path})
        df.to_csv(f"{new_path}/{filename}.csv", index=False)

        print("Total Contexts Generated - ", len(contexts), "\n")


if __name__ == '__main__':
    main()
