import json
import logging
from typing import Optional, Dict, Any
from groq import Groq
from app.config import settings

logger = logging.getLogger(__name__)

class GroqClient:
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        if not self.api_key:
            logger.error("GROQ_API_KEY is not configured in settings.")
            raise ValueError("GROQ_API_KEY is not set.")
        
        self.client = Groq(api_key=self.api_key)
        self.model_name = "llama-3.1-8b-instant"

    def extract_emotional_profile(self, prompt: str) -> Dict[str, Any]:
        """
        Send user prompt to Groq API and get structured emotional profile.
        Returns parsed dictionary of the response.
        """
        system_prompt = (
            "You are Vibe-Checker's Emotion Extraction Engine. Your job is to analyze "
            "natural language prompts from users describing their mood or emotional state, "
            "and output a structured JSON object representing their emotional profile.\n\n"
            "Analyze the input carefully:\n"
            "1. Classify the 'emotion_type' as one of:\n"
            "   - 'mixed_emotion': multiple concurrent emotions (e.g. happy but nostalgic)\n"
            "   - 'current_with_desired': user states how they feel and how they WANT to feel (e.g. feeling sad, need a lift)\n"
            "   - 'desired_only': user only states what they want to feel (e.g. play energetic music)\n"
            "   - 'current_only': user only states how they currently feel (e.g. I am angry)\n\n"
            "2. Infer and populate both 'current_state' and 'desired_state' state profiles. If only one state is described, "
            "make a reasonable logical inference to populate the other state.\n"
            "Each state profile must contain:\n"
            "   - 'primary_emotion': name of primary emotion (lowercase)\n"
            "   - 'secondary_emotion': name of secondary emotion or null\n"
            "   - 'energy' (float, 0.0 to 1.0): physical intensity (e.g. calm=0.2, high activity=0.8)\n"
            "   - 'valence' (float, 0.0 to 1.0): positivity (e.g. sad=0.1, neutral=0.5, happy=0.9)\n"
            "   - 'danceability' (float, 0.0 to 1.0): rhythm/groove matching the emotion\n"
            "   - 'acousticness' (float, 0.0 to 1.0): organic feel (e.g. reflective=0.8, workout=0.1)\n"
            "   - 'instrumentalness' (float, 0.0 to 1.0): vocal presence (e.g. focus/ambient=0.8, pop=0.1)\n"
            "   - 'tempo_range' (list of two floats): [min_bpm, max_bpm] (slow=60-90, medium=90-120, fast=120-180)\n\n"
            "3. Determine the 'transition' type: 'maintain', 'gradual', or 'immediate'.\n\n"
            "4. Provide a 'confidence' score (float, 0.0 to 1.0) for your extraction:\n"
            "   - For clear, specific emotional prompts (e.g. 'Feeling sad, need something slow to cheer me up'), confidence should be > 0.8\n"
            "   - For vague or short prompts (e.g. 'chill'), confidence should be 0.5 - 0.7\n"
            "   - For gibberish or nonsensical prompts (e.g. 'asdfjkl'), set confidence < 0.3 and perform a neutral best-effort mapping.\n\n"
            "Return ONLY a JSON object matching this schema, without any backticks, explanation, or extra text:\n"
            "{\n"
            "  \"emotion_type\": \"mixed_emotion | current_with_desired | desired_only | current_only\",\n"
            "  \"current_state\": {\n"
            "    \"primary_emotion\": \"string\",\n"
            "    \"secondary_emotion\": \"string\" or null,\n"
            "    \"energy\": float,\n"
            "    \"valence\": float,\n"
            "    \"danceability\": float,\n"
            "    \"acousticness\": float,\n"
            "    \"instrumentalness\": float,\n"
            "    \"tempo_range\": [float, float]\n"
            "  },\n"
            "  \"desired_state\": {\n"
            "    \"primary_emotion\": \"string\",\n"
            "    \"secondary_emotion\": \"string\" or null,\n"
            "    \"energy\": float,\n"
            "    \"valence\": float,\n"
            "    \"danceability\": float,\n"
            "    \"acousticness\": float,\n"
            "    \"instrumentalness\": float,\n"
            "    \"tempo_range\": [float, float]\n"
            "  },\n"
            "  \"transition\": \"maintain | gradual | immediate\",\n"
            "  \"confidence\": float\n"
            "}"
        )

        logger.info(f"Sending prompt to Groq model {self.model_name}")
        retries = 2
        for attempt in range(retries + 1):
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,  # Low temperature for deterministic structures
                    response_format={"type": "json_object"}
                )
                
                content = response.choices[0].message.content
                logger.debug(f"Groq API raw response: {content}")
                
                # Parse JSON
                profile_dict = json.loads(content)
                
                # Standardize casing for fields
                if "emotion_type" in profile_dict:
                    profile_dict["emotion_type"] = profile_dict["emotion_type"].lower()
                if "transition" in profile_dict:
                    # transition in model schema might be a string directly, 
                    # let's handle if transition is nested like {"type": "gradual"} or just a string
                    trans_val = profile_dict["transition"]
                    if isinstance(trans_val, dict) and "type" in trans_val:
                        profile_dict["transition"] = trans_val["type"]
                    elif not isinstance(trans_val, str):
                        profile_dict["transition"] = "maintain"
                else:
                    profile_dict["transition"] = "maintain"
                
                return profile_dict
                
            except json.JSONDecodeError as je:
                logger.warning(f"Attempt {attempt + 1}: Groq returned malformed JSON: {je}")
                if attempt == retries:
                    raise ValueError(f"Failed to parse Groq extraction response as JSON: {content}") from je
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1}: Groq API error: {e}")
                if attempt == retries:
                    raise e

    def generate_recommendation_explanation(self, prompt: str, profile_desc: str, tracks: list) -> str:
        """
        Generate a short explanation of why the selected tracks fit the prompt and emotional profile.
        """
        system_prompt = (
            "You are Vibe-Checker's Playlist Explainer. Your task is to write a warm, empathetic, "
            "and concise explanation (maximum 2 sentences, under 45 words) explaining why this playlist "
            "was selected for the user. Explain how the audio transition or qualities match the user's mood. "
            "Do not list individual track titles, but summarize the emotional journey or vibe."
        )
        
        # Format track summaries for LLM context
        tracks_summary = []
        for idx, t in enumerate(tracks[:6]): # summarize first few tracks to fit context and keep it fast
            tracks_summary.append(f"{t.track.track_name} by {t.track.artist} (Valence: {t.track.valence}, Energy: {t.track.energy})")
            
        user_message = (
            f"User Prompt: \"{prompt}\"\n"
            f"Emotional Profile Summary: {profile_desc}\n"
            f"Selected Tracks Sample: {', '.join(tracks_summary)}\n"
            "Provide the short explanation now:"
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=60
            )
            explanation = response.choices[0].message.content.strip()
            logger.info("Successfully generated AI recommendation explanation.")
            return explanation
        except Exception as e:
            logger.warning(f"Failed to generate AI explanation: {e}")
            return "These tracks were selected to match the emotional tones, energy shifts, and acoustic profile of your vibe prompt."

