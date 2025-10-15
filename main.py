import pyautogui
import pyperclip
import time
import os
from groq import Groq
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()


# Initialize Groq client with API key from environment
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


# Conversation history to maintain context
conversation_history = []


# System prompt to define bot behavior - customize this to match your style
conversation_history.append({
    "role": "system",
    "content": "You are replying to WhatsApp messages in a casual, friendly tone. Keep responses brief and natural, like a real person texting. Match the energy and style of incoming messages."
})


# Store the last message to avoid re-processing the same text
last_message = ""

# Counter to track API calls
api_call_count = 0

print("WhatsApp Auto-Reply Bot Starting...")
print("Make sure WhatsApp Web is open and visible on your screen")
time.sleep(3)


# Main loop - runs continuously to monitor and reply to messages
while True:
    try:
        # Step 1: Removed the click that was minimizing Chrome
        time.sleep(1)
        
        # Step 2: Select ONLY the last message (not entire chat)
        # IMPORTANT: Adjust these coordinates to select ONLY the most recent message
        pyautogui.moveTo(700, 800)  # Start from bottom area where latest message is
        pyautogui.dragTo(1889, 900, duration=0.5, button='left')  # Smaller selection
        time.sleep(0.5)
        
        # Step 3: Copy the selected text
        pyautogui.hotkey('ctrl', 'c')
        time.sleep(0.5)
        
        # Step 4: Get text from clipboard
        copied_text = pyperclip.paste()
        
        # Debug: Print what was copied
        print(f"[Debug] Copied text length: {len(copied_text)} chars")
        
        # Check if this is a new message (different from last processed message)
        if copied_text and copied_text != last_message and copied_text.strip() != "":
            # Additional check: skip if it's your own bot's message
            if copied_text == last_message:
                print("Skipping - same as last message")
                time.sleep(3)
                continue
                
            print(f"\n📩 New message received: {copied_text[:50]}...")
            
            # Add the incoming message to conversation history
            conversation_history.append({
                "role": "user",
                "content": copied_text
            })
            
            # Step 5: Get AI response from Groq
            print("🤖 Generating AI response...")
            api_call_count += 1
            print(f"[API Call #{api_call_count}]")
            
            chat_completion = client.chat.completions.create(
                messages=conversation_history,
                model="llama-3.3-70b-versatile",
                temperature=0.8,
                max_tokens=200,
                top_p=0.9
            )
            
            # Extract the reply text
            ai_reply = chat_completion.choices[0].message.content
            
            # Add AI's response to history for context
            conversation_history.append({
                "role": "assistant",
                "content": ai_reply
            })
            
            # Keep conversation history manageable (last 20 messages)
            if len(conversation_history) > 21:
                conversation_history = [conversation_history[0]] + conversation_history[-20:]
            
            print(f"✅ AI Reply: {ai_reply}")
            
            # Step 6: Click the message input field
            time.sleep(0.5)
            pyautogui.click(900, 980)
            time.sleep(0.5)
            
            # Step 7: Copy AI reply to clipboard and paste
            pyperclip.copy(ai_reply)
            time.sleep(0.3)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.5)
            
            # Step 8: Send the message
            pyautogui.press('enter')
            print("📤 Message sent!\n")
            
            # Update last message to the AI's reply
            last_message = ai_reply
            
            # Wait longer before checking for next message
            time.sleep(10)  # Increased to 10 seconds
        else:
            # No new message, wait and check again
            print("[Waiting for new message...]")
            time.sleep(5)
            
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        print("Retrying in 10 seconds...")
        time.sleep(10)
        continue
