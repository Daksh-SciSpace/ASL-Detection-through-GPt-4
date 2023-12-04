import cv2
import time
import requests
import json
import os
import base64


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
    

def get_response(image_path, api_key):

    base64_image = encode_image(image_path)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"""You are an expert in American Sign Language(ASL).\
                            In the given image, a person is making a sign in ASL and \
                            you need to identify what sign it is and also what is the \
                            meaning of that sign."""
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
        "max_tokens": 500,
        "temperature": 0,
        "top_p": 1.0,
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    result = response.json()
    model_response = result["choices"][0]["message"]["content"]

    return model_response


def capture_and_send_frame(interval_seconds, output_folder, api_key):

    cap = cv2.VideoCapture(0)
    frame_counter = 1

    while True:
        #capture single frame
        ret, frame = cap.read()

        if not ret:
            print("Failed to capture frame. Exiting...")
            break
        
        cv2.imshow('Live Feed', frame)

        #final frame path
        image_path = f"{output_folder}/Frame_{frame_counter}.png"

        #save frame
        cv2.imwrite(image_path, frame)
        print(f"Frame captured and saved as {image_path}")

        #send frame to GPT-4
        response = get_response(image_path, api_key)
        print(f"Model Response: {response}")

        frame_counter += 1

        time.sleep(interval_seconds)

        # 'q' the destroyer
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    #when everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()


# User Call that should be integrated with the internal API
interval_seconds = 7  # frame capture time interval
output_folder = "cap_frames"  # folder to save the frames

api_key = "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"
capture_and_send_frame(interval_seconds, output_folder, api_key)
