from pytube import Search, YouTube
from typing import List, Dict
from tools.youtube_tool import get_youtube_results

def available_tools() -> List[Dict]:
    return [
        {
            "type": "function",
            "function": {
                "name": "get_youtube_results",
                "description": "Search YouTube and get the top results based on the search string",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "search_string": {
                            "type": "string",
                            "description": "The search string to query YouTube",
                        }
                    },
                    "required": ["search_string"],
                },
            },
        }
    ]

def available_functions() -> Dict:
    return {
        "get_youtube_results": get_youtube_results
    }

