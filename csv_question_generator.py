import os
from pathlib import Path

import pandas as pd
from langchain.prompts import PromptTemplate
from langchain_community.llms import Ollama
from langchain_core.output_parsers import CommaSeparatedListOutputParser
from tqdm.auto import tqdm

CHUNK_SIZE = 512
MODEL_NAME = "mistral"
BASE_URL = "https://49ca-34-125-138-132.ngrok-free.app"


# BASE_URL = "http://127.0.0.1:11434"


def read_data(path):
    df = pd.read_csv(path)
    df.set_index(["Id"], inplace=True)
    return df


def get_qa_generation_prompt(text):
    return f"""Generate questions based on the below text chunk.
--------
{text}
--------"""


def generate_with_llm(chain, contexts_df: pd.DataFrame, context_ids: list, generated_qas_with_context, retry,
                      currentRetry):
    print(f"Current retry #{currentRetry}")

    if currentRetry >= retry:
        print(f"Retry Exceeded #{currentRetry}")
        return

    error_ids = []
    for _id in tqdm(context_ids):

        doc = contexts_df.loc[_id, "Context"]
        print(f"Processing #{_id} doc")
        try:
            result = chain.invoke({"query": get_qa_generation_prompt(doc)})
        except Exception as ex:
            print(f"Error #{_id} doc - {ex}")
            error_ids.append(_id)
            continue

        questions = result.split("?")
        for question in questions:
            qaPairJson = {}
            qaPairJson["contextId"] = _id
            qaPairJson["context"] = doc
            qaPairJson["question"] = f"{question.strip()}?"

            generated_qas_with_context.append(qaPairJson)

        print(f"Completed #{_id} doc")

    if len(error_ids) != 0:
        generate_with_llm(chain, contexts_df, error_ids, generated_qas_with_context, retry, currentRetry + 1)


def generate_qa(contexts: pd.DataFrame):
    jsonLLM = Ollama(
        model=MODEL_NAME,
        base_url=BASE_URL,
        # format="json"
    )

    parser = CommaSeparatedListOutputParser()
    # output_fixing_parser = OutputFixingParser.from_llm(parser=parser, llm=jsonLLM)

    prompt = PromptTemplate(
        template="\n{format_instructions}\n{query}",

        input_variables=["query"],
        partial_variables={"format_instructions": """
        Your response MUST be comma separated questions as values. All the questions MUST end with question mark. No Numbering or Bulletins allowed. \n
        Example: What is the code for AI program?, Tell me more about courses in AI program?, List all the programs in the George brown college? 
        """},

    )

    chain = prompt | jsonLLM

    # contexts_dict = {_id: doc for _id, doc in enumerate(contexts)}
    generated_qas_with_context = []

    generate_with_llm(chain, contexts, contexts.index, generated_qas_with_context,
                      3, 0)

    return generated_qas_with_context


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


def exclude_valid_creations(qaPairs_list, contexts_list):
    # Replace the starting paths
    # list1_replaced = [os.path.splitext(file)[0] for file in qaPairs_list]
    list2_replaced = [os.path.splitext(file.replace("qaPairs", "contexts", 1))[0] + ".csv" for file in
                      contexts_list]

    # Create sets after replacing starting paths
    set1_replaced = set(qaPairs_list)
    set2_replaced = set(list2_replaced)

    # Find files unique to each list after replacing starting paths
    return set1_replaced - set2_replaced


def get_empty_dfs(context_paths):
    return [path for path in context_paths if pd.read_csv(path).shape[0] == 0]


def main():
    files_list = get_files("contexts")
    already_created = get_files("qaPairs")
    invalid_creations = get_empty_dfs(already_created)

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

        new_path = "/".join(filepath.split("/")[:-1]).replace("contexts", "qaPairs")
        Path(new_path).mkdir(parents=True, exist_ok=True)

        contexts_df = read_data(path)
        qa_pairs = generate_qa(contexts_df)

        df = pd.DataFrame(qa_pairs)
        df.to_csv(f"{new_path}/{filename}.csv")

        print("Total Questions Generated - ", df.shape[0], "\n")


if __name__ == '__main__':
    main()
