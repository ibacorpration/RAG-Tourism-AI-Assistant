from app.services.memory.in_memory import InMemoryConversationMemory


def test_in_memory_conversation():
    memory = InMemoryConversationMemory(max_messages=4)
    conv_id = "test-session-1"

    memory.add_user_message(conv_id, "Hello")
    memory.add_ai_message(conv_id, "Hi there!")
    memory.add_user_message(conv_id, "What is RAG?")
    memory.add_ai_message(conv_id, "Retrieval Augmented Generation.")
    memory.add_user_message(conv_id, "Tell me more.")

    history = memory.get_history(conv_id)
    assert len(history) == 4
    assert history[0]["content"] == "Hi there!"
    assert history[-1]["content"] == "Tell me more."

    memory.clear_history(conv_id)
    assert len(memory.get_history(conv_id)) == 0
