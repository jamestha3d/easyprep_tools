import base64
import requests
import os
from dotenv import load_dotenv
import time
load_dotenv()
import json
import openai
from openai import OpenAI
import re

# OpenAI API Key
api_key = os.getenv("EASYPREP")

# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')


def identify_image(image_path):
    base64_image = encode_image(image_path)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
        }

    payload = {
    "model": "gpt-4o-mini",
    "messages": [
        {
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": "What is the name of this road sign? respond with only the sign name and nothing else"
            },
            {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
            }
            }
        ]
        }
    ],
    "max_tokens": 300
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    return response.json()


def generate_qa_for_sign(sign_name):
    print('Generating Questions for ', sign_name)
    prompt = f'Using the Ontario MTO handbook as a guide, Generate exactly 10 questions about {sign_name} in strict JSON format. Each question should have the following structure:'

    prompt += """ {
    "question": "The question text",
    "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
    "correct_answer": "The correct option",
    "explanation": "Explanation of why the correct answer is right"
    }

    The output should only be valid JSON. Do not include any text or comments outside the JSON structure. do not prefix with the word 'json'. your response should only be an array of jsons. """


    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ],
        "max_tokens": 1000,
    }

    headers = {
        "Content-Type": 'application/json',
        "Authorization": f'Bearer {api_key}'
    }

    response = requests.post(
        'https://api.openai.com/v1/chat/completions', headers=headers, data=json.dumps(payload)
    )

    if response.status_code == 200:
        # Extract the JSON response
        json_output = response.json()
        data = json_output['choices'][0]['message']['content']

        # Print or save the JSON output
        return data
    else:
        print('ERROR', response.text)
def process_images(folder_path, new_folder_path='webscraper/road_signs/'):
    count = 0
    # Ensure the directory exists, creating it if it does not
    if not os.path.exists(new_folder_path):
        os.makedirs(new_folder_path)
    json_folder = os.path.join(new_folder_path, "json")
    os.makedirs(json_folder, exist_ok=True)


    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        
        # Only process image files
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            try:
                # Identify the sign
                sign_name = identify_image(file_path)
                
                if 'choices' in sign_name:
                    print( filename, sign_name['choices'][0]['message']['content'])
                elif 'error' in sign_name:
                    print(filename, 'ERROR')
                else:
                    print(filename, sign_name)
                # Rename the image with the sign name
                image_name = f"{sign_name['choices'][0]['message']['content']}"
                friendly_image_name = image_name.replace(" ", "-")
                new_filename = f"{friendly_image_name}.jpg"
                count += 1
                try:
                    
                    new_file_path = os.path.join(new_folder_path, new_filename)
                    print(count, 'NEW FILE NAME', new_filename)

                    with open(file_path, 'rb') as source_image:
                        with open(new_file_path, 'w') as file:
                            file.write(source_image.read())
                except Exception as e:
                    print(e, new_folder_path)

                
                # Generate Q&A in JSON format
                # if 'sign' not in image_name and 'Sign' not in image_name and 'Signal':
                #     image_name += ' sign'
                if not re.search(r'\bsign\b', image_name, re.IGNORECASE):
                    image_name += ' Sign'
                qa_data = generate_qa_for_sign(image_name)
                json_file_path = os.path.join(json_folder, f"{image_name}.json")
                
                try:
                    qa_data = json.loads(qa_data)
                except Exception as e:
                    print(e, qa_data[0:100])
                    
                    
                # Save the JSON file
                with open(json_file_path, 'w', encoding='utf-8') as json_file:
                    json.dump(qa_data, json_file, indent=4)
                
                print(f"Processed: {new_filename}")
            
            except Exception as e:
                print(f"Failed to process {filename}: {str(e)}")
            timer()

def timer(countdown=21):
    for remaining in range(countdown, 0, -1):
        print(f"{remaining} s", end="\r")
        time.sleep(1)

if __name__ == '__main__':
    process_images('webscraper/signs')