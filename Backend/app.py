from agent import agent

print("=" * 50)
print("🏥 Hospital AI Assistant (Now with Memory!)")
print("=" * 50)

# 1. Start with an empty list to store the conversation
chat_history = []

while True:
    question = input("\nYou: ")

    if question.lower() in ["exit", "bye"]:
        print("Good Bye Take care!!!")
        break

    # 2. Invoke the agent with the past history PLUS the new question
    response = agent.invoke(
        {
            "messages": chat_history + [{"role": "user", "content": question}]
        }
    )

    # 3. Update our history to include the AI's new responses (and tool usage!)
    chat_history = response["messages"]

    # 4. Print the final answer to the user
    print("\nAssistant:")
    print(chat_history[-1].content)