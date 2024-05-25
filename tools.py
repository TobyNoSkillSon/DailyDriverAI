from pytube import Search, YouTube
from typing import List, Dict

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

def get_youtube_results(search_string: str, max_tokens: int = 4000):
    """Search YouTube and get the top results based on the search string"""
    print(f"Searching YouTube for: {search_string}")
    s = Search(search_string)
    results = s.results
    print(f"Found {len(results)} results")
    captions = []
    total_tokens = 0
    for result in results:
        print(f"Processing result: {result.watch_url}")
        yt = YouTube(result.watch_url)
        if yt.captions.keys():
            if 'en' in yt.captions:
                caption = yt.captions.get_by_language_code('en')
            else:
                print("English captions not found, using original language")
                caption = yt.captions.get_by_language_code(list(yt.captions.keys())[0])
            caption_srt = caption.generate_srt_captions()
            tokens = count_tokens(caption_srt)
            print(f"Caption length: {tokens} tokens")
            if total_tokens + tokens <= max_tokens:
                print("Adding captions to the result")
                captions.append(caption_srt)
                total_tokens += tokens
            else:
                print("Caption too long, skipping to next video")
                break
        else:
            print("No captions found for this video, skipping to next video")
    print(f"Total tokens used: {total_tokens}")
    return ' '.join(captions)

def count_tokens(captions: str) -> int:
    # TODO: Implement the function to count the number of tokens in the captions.
    # for now this is fine
    return len(captions) // 6

if __name__ == "__main__":
    # Test the get_youtube_results function
    search_string = "how to make a cheesecake"
    captions = get_youtube_results(search_string)
    print(captions)
