from langchain_core.messages import HumanMessage
from app.assistant.graph import build_graph


# Graph erstellen
graph = build_graph()


# Experiment 1: Name mitteilen
print("\n=== Experiment 1: Name mitteilen ===")

result_1 = graph.invoke({
    "messages": [
        HumanMessage(content="Ich heise Elvir Ibrahimovic"),
    ]
})

# Alle Nachrichten ausgeben
for message in result_1["messages"]:
    print(f"{message.type}: {message.content}")


# Experiment 2: Nach Namen fragen
print("\n=== Experiment 2: Nach Namen fragen ===")

# Vorherigen Gesprächsverlauf übernehmen
# und neue Nachricht hinzufügen
messages = result_1["messages"] + [
    HumanMessage(content="Wie heiße ich?")
]

result_2 = graph.invoke({
    "messages": messages
})

# Alle Nachrichten ausgeben
for message in result_2["messages"]:
    print(f"{message.type}: {message.content}")

