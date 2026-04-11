"""
Chatbot API Routes

Provides endpoints for the Help Bot NLP chatbot.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any
from app.services.chatbot import get_chatbot_response

router = APIRouter()


@router.post("/chat", response_model=Dict[str, Any])
async def chat_with_bot(message: str = Query(..., description="The message to send to the Help Bot")) -> Dict[str, Any]:
    """
    Send a message to the Help Bot

    The bot can help with:
    - How to use the application
    - Energy predictions for devices
    - Manual data input guidance
    - Device control information
    - Simulation scenarios
    - Analytics and reporting
    """
    if not message or not message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    try:
        response = get_chatbot_response(message.strip())
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chatbot error: {str(e)}")


@router.get("/chat/info", response_model=Dict[str, Any])
async def get_chatbot_info() -> Dict[str, Any]:
    """
    Get information about the Help Bot capabilities
    """
    return {
        "name": "Help Bot",
        "description": "Project assistant for Smart AI home energy analytics, forecasting, and cost guidance",
        "capabilities": [
            "Application usage guidance",
            "Device status and running-device checks",
            "Dataset count and data-quality verification",
            "Graph and chart explanation",
            "Manual data input help",
            "Energy predictions",
            "Past-data trend summaries",
            "Language and grammar help",
            "Rupee-based cost guidance",
        ],
        "example_queries": [
            "Hi",
            "How many datasets are there?",
            "What does the graph show?",
            "How do I use this app?",
            "Predict washing machine for 24 hours",
            "Which model is active?",
            "How can I reduce my BESCOM bill?",
            "How to add manual readings?",
            "Are all devices running?",
            "Summarize past data",
            "Help with grammar",
        ]
    }
