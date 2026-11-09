from langchain_core.messages import HumanMessage
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.checkpoint.memory import InMemorySaver

from app.assistant.graph import build_graph
from app.config import settings

print('\n=== Experiment 1: InMemory, gleicher Thread ===')
memory_graph = build_graph(checkpointer=InMemorySaver())
config_a = {'configurable': {'thread_id': 'thread-a'}}

memory_graph.invoke({'messages': [HumanMessage('Ich bin Elvir Ibrahimovic')]}, config_a)
ergebnis = memory_graph.invoke({'messages': [HumanMessage('Wie heiße ich?')]}, config_a)
print('Antwort:', ergebnis['messages'][-1].content)

print('\n=== Experiment 2: InMemory, anderer Thread ===')
config_b = {'configurable': {'thread_id': 'thread-b'}}

ergebnis = memory_graph.invoke({'messages': [HumanMessage('Wie heiße ich?')]}, config_b)
print('Antwort:', ergebnis['messages'][-1].content)

print('\n=== Experiment 3: Postgres, überlebt Neustart ===')

conn_string = settings.database_url.replace('+psycopg', '')
print('URL-Format ok:', conn_string.startswith('postgresql://'))

with PostgresSaver.from_conn_string(conn_string) as checkpointer:
    checkpointer.setup()

    graph = build_graph(checkpointer=checkpointer)
    config = {'configurable': {'thread_id': 'demo-postgres'}}

    gespeichert = graph.get_state(config).values.get('messages', [])

    if not gespeichert:
        print('Erster Start: ich stelle mich vor')
        graph.invoke({'messages': [HumanMessage('Ich heiße Elvir Ibrahimovic')]}, config)
    else:
        print(f'Weiterer Start: {len(gespeichert)} Nachrichten sind schon gespeichert')

    ergebnis = graph.invoke({'messages': [HumanMessage('Wie heiße ich?')]}, config)
    print('Antwort:', ergebnis['messages'][-1].content)
