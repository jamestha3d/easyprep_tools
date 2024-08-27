import base64
import requests
import os
from dotenv import load_dotenv
import time
load_dotenv()

# OpenAI API Key
api_key = os.getenv("EASYPREP")

# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

# # Path to your image
# image_path = "path_to_your_image.jpg"

# # Getting the base64 string
# base64_image = encode_image(image_path)

# headers = {
#   "Content-Type": "application/json",
#   "Authorization": f"Bearer {api_key}"
# }

# payload = {
#   "model": "gpt-4o-mini",
#   "messages": [
#     {
#       "role": "user",
#       "content": [
#         {
#           "type": "text",
#           "text": "What road sign is this?"
#         },
#         {
#           "type": "image_url",
#           "image_url": {
#             "url": f"data:image/jpeg;base64,{base64_image}"
#           }
#         }
#       ]
#     }
#   ],
#   "max_tokens": 300
# }

# response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)


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
    # print(response.json())
    return response.json()
    
def identify_image_openai(image_path, model="gpt-4o-mini"):
    from openai import OpenAI

    client = OpenAI()

    response = client.chat.completions.create(
    model= model,
    messages=[
        {
        "role": "user",
        "content": [
            {"type": "text", "text": "What’s in this image?"},
            {
            "type": "image_url",
            "image_url": {
                "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg",
            },
            },
        ],
        }
    ],
    max_tokens=300,
    )

    print(response.choices[0])


def process_images(folder_path):
    count = 0
    json_folder = os.path.join(folder_path, "json")
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
                # # Rename the image with the sign name
                # new_filename = f"{sign_name}.jpg"
                # new_file_path = os.path.join(folder_path, new_filename)
                # os.rename(file_path, new_file_path)
                
                # # Generate Q&A in JSON format
                # qa_data = generate_qa_for_sign(sign_name)
                # json_file_path = os.path.join(json_folder, f"{sign_name}.json")
                
                # # Save the JSON file
                # with open(json_file_path, 'w') as json_file:
                #     json.dump(qa_data, json_file, indent=4)
                
                # print(f"Processed: {new_filename}")
            
            except Exception as e:
                print(f"Failed to process {filename}: {str(e)}")
            timer()

#'choices': [{'index': 0, 'message': {'role': 'assistant', 'content': 'This road sign is typically referred to as a "street name sign" or "road name sign." It indicates the name of the road, which in this case is "Bowesville Road."', 'refusal': None}, 'logprobs': None, 'finish_reason': 'stop'}]

def timer(countdown=21):
    for remaining in range(countdown, 0, -1):
        # Print the remaining time
        print(f"{remaining} s", end="\r")
        # Sleep for 1 second
        time.sleep(1)

if __name__ == '__main__':
    process_images('webscraper/signs')