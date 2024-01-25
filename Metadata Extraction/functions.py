import numpy as np
import os
import json
import re
import pandas as pd
from langchain_community.llms import Ollama
from langchain_core.output_parsers import JsonOutputParser
from langchain.prompts import PromptTemplate
import logging

logger = logging.getLogger(__name__)


def Availability(full_scraped_data):
    try:
        # Split the full scraped data into lines
        lines = full_scraped_data.strip().split('\n')

        # Find indices where the specific headers are present
        header_indices = [i for i, line in enumerate(lines) if line in ["Program Availability", "Semester", "Domestic", "International"]]

        # Initialize json_output with a default value
        json_output = None
        
        # Iterate over each found header index
        for start_index in header_indices[::4]:
            # Check if all subsequent headers are present
            if all(header in lines[start_index:start_index + 4] for header in ["Semester", "Domestic", "International"]):
                # Extract the next 16 lines starting from the found index
                chunk_data = lines[start_index:start_index + 16]

                # Extract headers and data
                headers = chunk_data[:4]
                data = [chunk_data[j:j + 4] for j in range(4, len(chunk_data), 4)]

                # Create a list to store the sentences
                sentences = []

                # Iterate over the data and create sentences
                for k in range(len(data)):
                    semester_year = f"{data[k][0]} {data[k][1]}"
                    domestic_availability = f"{semester_year} Domestic {data[k][2].lower()}"
                    international_availability = f"{semester_year} International {data[k][3].lower()}"
                    
                    sentences.extend([domestic_availability, international_availability])

                # Convert to DataFrame
                columns = ['Semester', 'Year', 'Intake', 'Availability']
                data_for_df = [sentence.split()[:3] + [' '.join(sentence.split()[3:])] for sentence in sentences]
                df = pd.DataFrame(data_for_df, columns=columns)

                # Convert DataFrame to JSON
                json_output = json.loads(df.to_json(orient='records'))

        return json_output
    except Exception as e:
        logger.error(f"Error in Availability: {e}")
        return None


def program_info1(scraped_data):
    try:
        # Define a regex pattern to match key-value pairs
        pattern = re.compile(r'([^:\n]+):\s*([^\n]+)')

        # Search for the Program Name to Program Availability subset
        subset_match = re.search(r'Program Name:.*Program Availability', scraped_data, re.DOTALL)

        if subset_match:
            # Find matches in the subset
            matches = pattern.findall(subset_match.group())

            # Create a dictionary from the matches
            metadata_dict = dict(matches)
            
            return metadata_dict
        else:
            return None  # Return None if the subset is not found
    except Exception as e:
        logger.error(f"Error in program_info1: {e}")
        return None
    
def extract_contact_chunk(full_scraped_data):
    try:
        # Find the starting index of the "Contact Us" section
        start_index1 = full_scraped_data.find(".\nContact Us")
        start_index2 = full_scraped_data.find('English assessment\nContact Us')
        start_index3 = full_scraped_data.find('Contact Us\nContact')

        # Choose the minimum valid start index
        valid_start_indices = [index for index in [start_index1, start_index2, start_index3] if index != -1]
        if not valid_start_indices:
            return None  # Return None if no valid start index is found

        start_index = min(valid_start_indices)

        # Find the ending index of the "Visit" section
        end_index1 = full_scraped_data.find("Visit", start_index)
        end_index2 = full_scraped_data.find("For more information about George Brown College", start_index)

        # Choose the minimum valid end index
        valid_end_indices = [index for index in [end_index1, end_index2] if index != -1]
        if not valid_end_indices:
            return None  # Return None if no valid end index is found

        end_index = min(valid_end_indices)

        # Extract the chunk between start and end indices
        contact_chunk = full_scraped_data[start_index:end_index].strip()

        # Remove the first line if it doesn't contain "English assessment" or "."
        lines = contact_chunk.split('\n')
        if lines and not any(keyword in lines[0] for keyword in ['Contact Us']):
            lines = lines[1:]

        return '\n'.join(lines)
    except Exception as e:
        logger.error(f"Error in extract_contact_chunk: {e}")
        return None

def extract_contact(base_url1,chunk):
    try:
        prompt_temp1 = """"
        You are an intelligent AI model designed to convert text into structured JSON format. Your mission is to extract essential information from the provided text and output it as a well-organized JSON object. Your response should exclusively consist of the JSON representation without any additional text. Review the following examples for guidance:

        Example 1:

        Input:
        Contact Us
        School of Deaf and Deafblind Studies
        Email:
        communityservices@georgebrown.ca
        Our office hours are 8 a.m. – 4 p.m.
        Erika Stebbings, ASL & Deaf Studies Program Co-ordinator
        Email:
        erika.stebbings@georgebrown.ca

        Output:
        {
        "Contact": "School of Deaf and Deafblind Studies",
        "Contact email": "communityservices@georgebrown.ca",
        "Office Hours": "8 a.m. – 4 p.m",
        "Program Co-ordinator": "Erika Stebbings",
        "Co-ordinator email": "erika.stebbings@georgebrown.ca"
        }

        Example 2:

        Input:
        Contact Us
        School of Computer Technology
        Phone: 416-415-5000, ext. 4287
        Email:
        computertechnology@georgebrown.ca
        The office hours are:
        Monday – Friday: 9 a.m. – 4 p.m.
        Program Co-ordinator: Moe Fadaee
        Email:
        Moe.Fadaee@georgebrown.ca
        Phone: 416-415-5000, ext. 3229

        Output:
        {
        "Contact": "School of Computer Technology",
        "Contact email": "computertechnology@georgebrown.ca",
        "Phone": "416-415-5000, ext. 4287",
        "Office Hours": "Monday – Friday: 9 a.m. – 4 p.m.",
        "Program Co-ordinator": "Moe Fadaee",
        "Co-ordinator email": "Moe.Fadaee@georgebrown.ca",
        "Co-ordinator Phone": "416-415-5000, ext. 3229"
        }

        Now, extract the key information from the following text:"""
        llm1 =  Ollama(
        model="mistral",
        base_url=base_url1
        )

        parser = JsonOutputParser()
        prompt = PromptTemplate(
            template="{prompt_temp}.\n{query}\n\n {format_instructions}",
            input_variables=["query"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        chain = prompt | llm1 | parser

        contact_info = chain.invoke({ "prompt_temp":prompt_temp1 ,"query": chunk })
        return contact_info
    except Exception as e:
        logger.error(f"Error in extract_contact: {e}")
        prompt2 = """You are a proficient AI text summarizer with a focus on extracting key information about contact details. Summarize the given text, highlighting essential information related to contact details in just two concise lines. Ensure that the summary effectively conveys the primary details, such as contact names, email addresses, phone numbers, and any notable office hours or positions.
         Now, extract the key information from the following text:
         
         """
        llm1 =  Ollama(
        model="mistral",
        base_url=base_url1
        )
        return str(llm1.invoke(prompt2+chunk))

# Function to extract information from the scraped data
def extract_info(data,base_url1):
    try:
        program_info = {}
        
        # Extract Program Information
        program_info["Program Information"] = program_info1(data)
        
        
        # Extract Program Availability
        program_info['Availability'] =Availability(data)
        
        contact_chunk = extract_contact_chunk(data)
 
        program_info['Contact Related Information'] = extract_contact(base_url1,contact_chunk)

        return program_info
    except Exception as e:
        logger.error(f"Error in extract_info: {e}")
        return None
    
def process_text_file(file_path, metadata_folder,base_url1):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            full_scraped_data = file.read()

        file_name = os.path.splitext(os.path.basename(file_path))[0]  # Get the filename without extension
        metadata_file_path = os.path.join(metadata_folder, f"{file_name}.json")

        # Extract information
        extracted_info = extract_info(full_scraped_data,base_url1)


        # Save extracted information to JSON file in metadata folder
        with open(metadata_file_path, 'w', encoding='utf-8') as json_file:
            json.dump(extracted_info, json_file, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error in process_text_file for {file_path}: {e}")
