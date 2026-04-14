from app.services.chatbot import get_chatbot_response


def test_chatbot_dataset_files_intent():
    data = get_chatbot_response("list available datasets")
    assert data.get("intent") == "dataset_files"
    assert "Available CSV datasets" in data.get("response", "")
    assert isinstance(data.get("suggestions"), list)


def test_chatbot_dataset_mode_intent():
    data = get_chatbot_response("which dataset mode is active")
    assert data.get("intent") == "dataset_mode"
    assert "Current dataset configuration" in data.get("response", "")


def test_chatbot_grammar_rewrite_intent():
    data = get_chatbot_response("rewrite: my project predict energy and save bill")
    assert data.get("intent") == "grammar"
    assert "Rewritten version" in data.get("response", "")


def test_chatbot_language_detection_non_english():
    data = get_chatbot_response("language: मेरा प्रोजेक्ट ऊर्जा उपयोग का विश्लेषण करता है")
    assert data.get("intent") == "language"
    assert "Detected language" in data.get("response", "")


def test_chatbot_grammar_diagnostics_present():
    data = get_chatbot_response("grammar: i  cant reduce my bill")
    assert data.get("intent") == "grammar"
    assert "Grammar review" in data.get("response", "")
    assert "Detected language" in data.get("response", "")


def test_chatbot_session_memory_followup():
    session_id = "test-memory-session"
    first = get_chatbot_response("how many datasets are there?", session_id=session_id)
    followup = get_chatbot_response("more details", session_id=session_id)
    assert first.get("session_id") == session_id
    assert followup.get("session_id") == session_id
    assert followup.get("intent") in {"dataset_info", "dataset_files", "dataset_mode"}


def test_chatbot_kannada_project_response():
    data = get_chatbot_response("about project in kannada")
    assert data.get("intent") == "language"
    assert "ಈ ಪ್ರಾಜೆಕ್ಟ್" in data.get("response", "")


def test_chatbot_device_explain_intent():
    data = get_chatbot_response("what is fan")
    assert data.get("intent") == "device_explain"
    assert "fan" in data.get("response", "").lower()


def test_chatbot_today_device_consumption_intent():
    data = get_chatbot_response("what is todays fan energy consemtion")
    assert data.get("intent") == "device_today_consumption"
    response_text = data.get("response", "").lower()
    assert "today" in response_text
    assert "fan" in response_text
