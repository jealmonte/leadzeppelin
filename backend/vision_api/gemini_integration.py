"""
Simple Google Gemini integration to map parsed letter notes to shapes.

This module contains a helper `map_notes_to_shapes` which accepts a list-of-lists
of note tokens (output of `parse_letter_notes_from_url`) and returns a JSON-like
mapping from notes to shapes. The function uses the Google Generative AI (Gemini)
HTTP API via the official `google-genai` Python client.

Important: To use Google Gemini you'll need to enable the Generative AI API in
your Google Cloud project and provide credentials (see GEMINI_README.md).

This file intentionally keeps the call optional so tests and offline runs don't
require network or credentials.
"""

from dotenv import load_dotenv
import os
import json
from google import genai

load_dotenv()  # Load environment variables from .env file

def map_notes_to_shapes(parsed_notes):
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        raise ValueError("Missing GOOGLE_API_KEY environment variable")
    
    client = genai.Client(api_key=api_key)

    notes_text = '\n'.join([' '.join(line) for line in parsed_notes])
    prompt = (
        f"Convert these piano letter notes into simple geometric or hand-drawable shapes "
        f"that a computer vision system can detect. Return ONLY a JSON dictionary mapping notes to shapes, nothing else:\n{notes_text}\n\n"
        f"Example format: {{\"C\": \"circle\", \"D\": \"triangle\", \"E\": \"square\"}}"
    )
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        
        # Debug: Print the raw response
        print("Raw Gemini response:", response.text)
        
        # Try to clean the response if it contains extra text
        response_text = response.text.strip()
        
        # Look for JSON content between curly braces
        import re
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            json_text = json_match.group()
            print("Extracted JSON:", json_text)
            return json.loads(json_text)
        else:
            print("No JSON found in response")
            return {"error": f"No JSON found in response: {response_text[:200]}..."}
            
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        print(f"Failed to parse: {response.text[:200]}...")
        return {"error": f"Could not parse Gemini response as JSON: {str(e)}"}
    except Exception as e:
        print(f"Gemini API error: {e}")
        return {"error": f"Gemini API error: {str(e)}"}
    
def generate_lesson_plan(parsed_notes, shapes, song_title="Unknown Song", difficulty="beginner"):
    """
    Generate a structured lesson plan for beginners based on parsed notes and shape mappings.
    
    Args:
        parsed_notes (list): List of note sequences from parse_letter_notes_from_url
        shapes (dict): Note-to-shape mappings from map_notes_to_shapes  
        song_title (str): Name of the song being learned
        difficulty (str): Lesson difficulty level (default: "beginner")
    
    Returns:
        dict: Structured lesson plan with exercises and instructions
    """
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        raise ValueError("Missing GOOGLE_API_KEY environment variable")
    
    client = genai.Client(api_key=api_key)
    
    # Extract unique notes and create teaching context
    unique_notes = set()
    for line in parsed_notes:
        unique_notes.update(line)
    
    notes_summary = list(unique_notes)
    note_sequences = [' -> '.join(line) for line in parsed_notes[:3]]  # First 3 sequences
    
    # Create comprehensive prompt for lesson planning
    prompt = f"""
Create a structured beginner music lesson plan for learning "{song_title}".

SONG ANALYSIS:
- Notes used: {', '.join(sorted(notes_summary))}
- Note sequences: {'; '.join(note_sequences)}
- Visual shapes: {shapes}

REQUIREMENTS:
Generate a JSON lesson plan with these sections:
1. "lesson_overview": Brief description and learning objectives
2. "warm_up_exercises": 3 simple exercises to prepare
3. "note_introduction": Step-by-step introduction of each new note
4. "shape_associations": How to use visual shapes for learning
5. "practice_steps": Progressive practice exercises (5 steps)
6. "common_mistakes": What beginners typically struggle with
7. "success_tips": Encouragement and helpful hints
8. "estimated_time": Total lesson duration in minutes

Make it encouraging, age-appropriate for beginners, and incorporate the visual shape system.
Return ONLY valid JSON, no extra text.
"""

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        
        print("Raw lesson plan response:", response.text)
        
        # Extract JSON from response
        import re
        json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if json_match:
            json_text = json_match.group()
            return json.loads(json_text)
        else:
            return {"error": f"No JSON found in lesson plan response: {response.text[:200]}..."}
            
    except json.JSONDecodeError as e:
        print(f"Lesson plan JSON decode error: {e}")
        return {"error": f"Could not parse lesson plan response: {str(e)}"}
    except Exception as e:
        print(f"Lesson plan API error: {e}")
        return {"error": f"Lesson plan generation error: {str(e)}"}

def generate_encouragement_feedback(expected_note, played_note, attempt_count=1):
    """
    Generate supportive feedback when learner plays wrong note.
    
    Args:
        expected_note (str): The note that should have been played
        played_note (str): The note that was actually played  
        attempt_count (int): How many times they've tried this note
    
    Returns:
        dict: Encouraging feedback and guidance
    """
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        return {"message": "That's okay! Try again.", "restart": True}
    
    client = genai.Client(api_key=api_key)
    
    prompt = f"""
Generate encouraging, supportive feedback for a beginner piano learner.

SITUATION:
- Expected note: {expected_note}
- Played note: {played_note}
- Attempt number: {attempt_count}

Create a JSON response with:
1. "message": Encouraging message (keep positive, age-appropriate)
2. "tip": Helpful hint about the correct note
3. "restart": true (to allow them to start over)
4. "motivation": Brief motivational phrase

Make it sound like a supportive teacher, not discouraging. Focus on learning.
Return ONLY valid JSON.
"""

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        
        import re
        json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        else:
            return {
                "message": "Great try! Let's practice that note again.",
                "tip": f"Remember, you're looking for the {expected_note} note.",
                "restart": True,
                "motivation": "Every musician learns by practicing!"
            }
            
    except Exception as e:
        return {
            "message": "That's perfectly fine! Let's try again.",
            "tip": f"Focus on finding the {expected_note} note shape.",
            "restart": True, 
            "motivation": "You're learning something new!"
        }

def get_note_sequence_for_demo(parsed_notes, shapes):
    """
    Extract clean note sequence for demo mode - just the notes in order.
    
    Args:
        parsed_notes (list): Parsed note sequences
        shapes (dict): Note-to-shape mappings
        
    Returns:
        dict: Clean sequence for demo mode
    """
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        # Fallback: return first sequence
        if parsed_notes:
            return {"demo_sequence": parsed_notes[0], "shapes": shapes}
        return {"demo_sequence": [], "shapes": shapes}
    
    client = genai.Client(api_key=api_key)
    
    prompt = f"""
Create a clean demo sequence for piano computer vision demonstration.

PARSED NOTES: {parsed_notes}
SHAPES: {shapes}

Extract the main melody line (usually the first or most complete sequence) and return:
{{
  "demo_sequence": ["note1", "note2", "note3", ...],
  "instructions": "Play each note when the corresponding shape lights up",
  "shapes": {shapes}
}}

Choose the sequence that would make the best demo - clear, recognizable melody.
Return ONLY valid JSON.
"""

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash', 
            contents=prompt
        )
        
        import re
        json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        else:
            # Fallback 
            return {
                "demo_sequence": parsed_notes[0] if parsed_notes else [],
                "instructions": "Play each note when the corresponding shape appears",
                "shapes": shapes
            }
            
    except Exception as e:
        return {
            "demo_sequence": parsed_notes[0] if parsed_notes else [],
            "instructions": "Follow the shapes to play the melody",
            "shapes": shapes
        }

    
