import ollama

SYSTEM_PROMPT = """You are TechCoder CLI, an expert coding assistant. 
You help developers write, debug, and improve code.

Your rules:
- Always provide clean, working code
- Explain your code clearly
- Suggest best practices
- If asked something unrelated to coding, politely redirect to coding topics
"""

def chat(messages):
    response = ollama.chat(
        model='gemma4:e4b',
        messages=messages
    )
    return response['message']['content']

def main():
    print("🤖 TechCoder CLI - Powered by Gemma 4")
    print("Your personal coding assistant. Type 'exit' to quit\n")
    
    # History chat dimulai dengan system prompt
    messages = [
        {'role': 'system', 'content': SYSTEM_PROMPT}
    ]
    
    while True:
        user_input = input("You: ")
        
        if user_input.lower() == 'exit':
            print("Bye! Happy coding! 👋")
            break
        
        # Tambah pesan user ke history
        messages.append({'role': 'user', 'content': user_input})
        
        print("\n🤖 Gemma: Thinking...\n")
        response = chat(messages)
        
        # Tambah response ke history
        messages.append({'role': 'assistant', 'content': response})
        
        print(f"🤖 Gemma: {response}\n")

if __name__ == "__main__":
    main()