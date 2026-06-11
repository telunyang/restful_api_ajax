import asyncio
from ollama import AsyncClient
import time


async def recognize():
    t1 = time.time()

    image_path = "D:\\teach\\restful_api_ajax\\ollama\\example01.jpg"

    messages = [
        {
            'role': 'user', 
            'content': '請描述這張圖片的內容。',
            'images': [image_path] # 可以多張圖片，格式為 List[str]，每個元素為圖片的路徑
        }
    ]

    client = AsyncClient(
        host='http://localhost:11434',
        timeout=600
    )
    
    response = await client.chat(
        model='qwen3.5:0.8b', 
        messages=messages,
        keep_alive="1h",
        think=False,
        options={
            "temperature": 1.0,
            "top_k": 64,
            "top_p": 0.95
        },
    )
    print(response.message.content)

    t2 = time.time()
    print(f"Response time: {t2 - t1:.2f} seconds")


# 測試 ollama 辨識功能 (streaming)
'''
async def recognize_stream():
    t1 = time.time()

    # 圖片辨識測試，請確保 ollama 模型支援圖片輸入，並且圖片路徑正確
    image_path = './example01.jpg'
    img = cv2.imread(image_path)
    success, encoded_img = cv2.imencode('.jpg', img)
    if success:
        image_bytes = encoded_img.tobytes()
    else:
        print("Failed to read or encode the image.")
        return

    messages = [
        {
            'role': 'user', 
            'content': '請形容這張圖片的內容，其中有一個物件上面寫著字，請問上面寫什麼？',
            'images': [image_bytes] # 可以多張圖片，格式為 List[bytes]，每個元素為圖片的二進位數據
        }
    ]

    stream = await AsyncClient(
        host='http://localhost:11434',
        timeout=600
    ).chat(
        model='qwen3.5:0.8b', 
        messages=messages,
        keep_alive="1h",
        stream=True
    )
    async for part in stream:
        print(part['message']['content'], end='', flush=True)
    t2 = time.time()
    print(f"Response time: {t2 - t1:.2f} seconds")
'''

if __name__ == "__main__":
    asyncio.run(recognize())