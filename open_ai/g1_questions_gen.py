import os
import requests
import openai
import os
from PIL import Image
import json

# Set your OpenAI API key
openai.api_key = 'your_openai_api_key_here'
# Define your OpenAI API key
api_key = 'your_openai_api_key_here'

# Define the folder containing images
image_folder = '/path/to/your/image/folder'

# Define the endpoint for uploading images and generating responses
api_url = 'https://api.openai.com/v1/images/generate'  # Replace with the correct endpoint

def upload_image_and_get_response(image_path):
    with open(image_path, 'rb') as image_file:
        response = requests.post(
            api_url,
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/octet-stream'
            },
            data=image_file
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to get response for {image_path}: {response.status_code}, {response.text}")
            return None

def process_images_in_folder(folder_path):
    for image_name in os.listdir(folder_path):
        image_path = os.path.join(folder_path, image_name)
        if os.path.isfile(image_path) and image_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            print(f"Processing image: {image_name}")
            response = upload_image_and_get_response(image_path)
            
            if response:
                # Assume the API returns the name of the image and some questions/answers
                image_name_from_ai = response.get('image_name', 'Unknown Name')
                questions_and_answers = response.get('qa_pairs', [])
                
                print(f"Image Name: {image_name_from_ai}")
                for i, (question, answer) in enumerate(questions_and_answers, start=1):
                    print(f"Q{i}: {question}")
                    print(f"A{i}: {answer}")
            print("--------")

# Run the script
process_images_in_folder(image_folder)




def get_image_name(image_path):
    """
    Send image details to OpenAI to ask for the name of the image.
    """
    try:
        # Create a description prompt for the image
        prompt = f"Look at this image and describe the traffic sign: {image_path}"
        
        # Call ChatGPT to describe the image
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=50
        )

        # Extract the name from the response
        image_name = response.choices[0].text.strip()
        return image_name

    except Exception as e:
        print(f"Error fetching image name: {e}")
        return None

def create_json_data(image_name):
    """
    Generate JSON with questions and answers about the image.
    """
    data = {
        "image_name": image_name,
        "questions": [
            {
                "question": f"What is the meaning of {image_name}?",
                "answer": f"The {image_name} sign indicates..."
            },
            {
                "question": f"In what situation would you see the {image_name}?",
                "answer": f"You would see the {image_name} sign when..."
            }
        ]
    }

    # Save the data to a JSON file
    with open(f"{image_name}.json", "w") as json_file:
        json.dump(data, json_file, indent=4)

def rename_image(image_path, new_name):
    """
    Rename the image based on the AI's provided name.
    """
    try:
        directory, original_name = os.path.split(image_path)
        file_extension = original_name.split('.')[-1]
        new_image_path = os.path.join(directory, f"{new_name}.{file_extension}")
        os.rename(image_path, new_image_path)
        print(f"Image renamed to: {new_image_path}")
        return new_image_path

    except Exception as e:
        print(f"Error renaming image: {e}")
        return None

def process_images(image_folder):
    """
    Process each image in the folder: Get name, rename image, and create JSON file.
    """
    for filename in os.listdir(image_folder):
        image_path = os.path.join(image_folder, filename)
        if filename.lower().endswith(('png', 'jpg', 'jpeg')):
            # Get the image name from ChatGPT
            image_name = get_image_name(image_path)
            if image_name:
                # Rename the image
                new_image_path = rename_image(image_path, image_name)
                if new_image_path:
                    # Create the corresponding JSON
                    create_json_data(image_name)

# Set your image folder path
image_folder_path = 'path_to_your_image_folder'
process_images(image_folder_path)
