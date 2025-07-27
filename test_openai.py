import os
from dotenv import load_dotenv

# Load environment variables from .env file FIRST
load_dotenv()

# NOW you can import other modules that depend on the environment variables
import asyncio
from services.openai_service import openai_service

async def main():
    print("Testing OpenAI integration...")
    test_data = {
        'brand_name': 'SustainaWear',
        'topic': 'Launch of our new eco-friendly sneaker',
        'tone': 'modern',
        'brief': 'A stylish sneaker made from recycled ocean plastic.',
        'target_audience': 'Eco-conscious millennials'
    }
    
    try:
        print("\n--- Generating Caption ---")
        caption = await openai_service.generate_caption(test_data)
        print(caption)
        
        print("\n--- Generating Image ---")
        image_url = await openai_service.generate_image(test_data)
        print(f"Image URL: {image_url}")
        
        print("\n✅ OpenAI service test successful!")
    except Exception as e:
        print(f"\n❌ Test Failed: {e}")

if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set.")
    else:
        asyncio.run(main())