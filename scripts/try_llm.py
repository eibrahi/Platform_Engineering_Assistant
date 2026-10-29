from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from app.llm import get_chat_model

model = get_chat_model()

system = SystemMessage("Du bist ein erfahrener Data Engineer.")
print('\n=== Experiment 1: erste Antwort ===')
antwort_a = model.invoke([
    system,
    HumanMessage("Ich heiße Elvir Elvirovic")
])
print(antwort_a.content)
print(antwort_a.usage_metadata)

print('\n=== Experiment 2: ohne Gedächtnis ===')
antwort_b = model.invoke([
    system,
    HumanMessage("Wie heiße ich?")
])
print(antwort_b.content)
print(antwort_b.usage_metadata)

print('\n=== Experiment 3: Gedächtnis von Hand ===')
antwort_c = model.invoke([
    system,
    HumanMessage("Ich heiße ..."), antwort_a, HumanMessage("Wie heiße ich?")
])
print(antwort_c.content)
print(antwort_c.usage_metadata)
