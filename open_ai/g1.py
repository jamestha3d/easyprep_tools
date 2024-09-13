import os
import openai
import json
from PIL import Image
from dotenv import load_dotenv
from openai import OpenAI


# Load environment variables from .env file
load_dotenv()

# Set up your OpenAI API key
openai.api_key = os.getenv("OPEN_AI_API_KEY")  # Or replace with your actual API key

def identify_sign(image_path):
    # Open the image file
    with open(image_path, 'rb') as img_file:
        img_data = img_file.read()

    # Make an API call to OpenAI with the image data
    response = openai.Image.create_completion(
        model="gpt-4o-mini",  # Replace with the appropriate model if needed
        prompt="What is the name of this traffic sign?",
        files={"file": img_data},
        n=1,
        stop=None,
        max_tokens=10
    )

    # Extract the name of the sign from the response
    sign_name = response.choices[0].text.strip()
    print(sign_name)
    return sign_name

def generate_qa_for_sign(sign_name):
    # Make an API call to OpenAI to generate questions and answers
    prompt = f"Generate questions and answers about the {sign_name} traffic sign."
    
    response = openai.Completion.create(
        engine="text-davinci-003",  # Use the appropriate model for text generation
        prompt=prompt,
        max_tokens=150
    )

    qa_data = json.loads(response.choices[0].text.strip())
    return qa_data

def process_images(folder_path):
    json_folder = os.path.join(folder_path, "json")
    os.makedirs(json_folder, exist_ok=True)

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        
        # Only process image files
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            try:
                # Identify the sign
                sign_name = identify_sign(file_path)
                
                # Rename the image with the sign name
                new_filename = f"{sign_name}.jpg"
                new_file_path = os.path.join(folder_path, new_filename)
                os.rename(file_path, new_file_path)
                
                # Generate Q&A in JSON format
                qa_data = generate_qa_for_sign(sign_name)
                json_file_path = os.path.join(json_folder, f"{sign_name}.json")
                
                # Save the JSON file
                with open(json_file_path, 'w') as json_file:
                    json.dump(qa_data, json_file, indent=4)
                
                print(f"Processed: {new_filename}")
            
            except Exception as e:
                print(f"Failed to process {filename}: {str(e)}")


def open_ai_connect():
    client = OpenAI(
        organization='',
        project='$PROJECT'
    )
# Define the path to the folder containing the images
folder_path = 'path_to_signs_folder'

# Process all images in the folder
process_images(folder_path)

