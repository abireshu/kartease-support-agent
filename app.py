from agent import agent, ask_with_tools

def main():
    print("=== KartEase Support Agent Chat ===")
    print("Type 'exit' or 'quit' to end the session.\n")
    
    while True:
        try:
            question = input("You: ").strip()
            if not question:
                continue
            if question.lower() in ["exit", "quit"]:
                print("Goodbye! Thank you for using KartEase support.")
                break
                
            answer, tools_used = ask_with_tools(agent, question)
            print(f"\nAgent: {answer}")
            print(f"[Tools used: {', '.join(tools_used) if tools_used else 'none'}]\n")
            
        except (KeyboardInterrupt, EOFError):
            print("\nSession ended.")
            break

if __name__ == "__main__":
    main()