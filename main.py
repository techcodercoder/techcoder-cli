import ollama

def chat(user_input):
    response = ollama.chat(
        model='gemma4:e4b',
        messages=[{'role': 'user', 'content': user_input}]
    )
    return response['message']['content']

def main():
    print("🤖 TechCoder CLI - Powered by Gemma 4")
    print("Type 'exit' to quit\n")
    
    while True:
        user_input = input("You: ")
        
        if user_input.lower() == 'exit':
            print("Bye! 👋")
            break
            
        print("\n🤖 Gemma: Thinking...\n")
        response = chat(user_input)
        print(f"🤖 Gemma: {response}\n")

if __name__ == "__main__":
    main()