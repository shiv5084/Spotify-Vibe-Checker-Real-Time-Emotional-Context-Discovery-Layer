import logging
from typing import List, Dict, Any
from app.services.qdrant_client import QdrantService
from app.models.emotion import EmotionalProfile, StateProfile
from app.models.track import Track, CandidateTrack
from supabase import create_client, Client
from app.config import settings
from fastembed import TextEmbedding

logger = logging.getLogger(__name__)

class SemanticRetriever:
    def __init__(self, qdrant_service: QdrantService):
        self.qdrant = qdrant_service
        self.embedding_model = TextEmbedding(model_name=settings.EMBEDDING_MODEL)
        self.supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

    def retrieve(self, profile: EmotionalProfile) -> List[CandidateTrack]:
        """
        Convert EmotionalProfile to text queries, embed them, search Qdrant,
        and enrich results using metadata from Supabase PostgreSQL.
        
        Args:
            profile: Emotional profile model.
            
        Returns:
            List of CandidateTrack objects.
        """
        logger.info(f"Retrieving candidate tracks for emotion type: {profile.emotion_type}")

        # 1. Formulate search queries for current and (optional) desired states
        queries = []
        queries.append(self._state_to_query_text(profile.current))
        if profile.desired:
            queries.append(self._state_to_query_text(profile.desired))

        # 2. Search Qdrant for each query
        qdrant_results = {}
        for query_text in queries:
            logger.info(f"Generating embedding & searching Qdrant for query: '{query_text}'")
            try:
                # Generate query embedding
                query_vector = next(self.embedding_model.embed([query_text])).tolist()
                
                # Cosine search in Qdrant (top 50)
                points = self.qdrant.search_similar_tracks(query_vector, limit=50)
                for point in points:
                    track_id = point.payload.get("track_id")
                    if track_id:
                        # Keep the highest similarity score if duplicate across searches
                        qdrant_results[track_id] = max(qdrant_results.get(track_id, 0.0), point.score)
            except Exception as e:
                logger.error(f"Qdrant search failed for query '{query_text}': {e}")
                
        if not qdrant_results:
            logger.warning("No candidate track IDs returned from Qdrant.")
            return []

        # 3. Enrich with metadata from Supabase PostgreSQL
        track_ids = list(qdrant_results.keys())
        logger.info(f"Fetching metadata from Supabase for {len(track_ids)} unique track IDs...")
        
        enriched_candidates = []
        try:
            res = self.supabase.table("tracks").select("*").in_("id", track_ids).execute()
            db_tracks = res.data
            
            # Map database records to Pydantic Track objects
            for db_track in db_tracks:
                try:
                    track_obj = Track(**db_track)
                    score = qdrant_results[track_obj.id]
                    enriched_candidates.append(CandidateTrack(
                        track=track_obj,
                        similarity_score=score
                    ))
                except Exception as val_err:
                    logger.warning(f"Failed to validate track metadata for ID {db_track.get('id')}: {val_err}")
        except Exception as e:
            logger.error(f"Supabase metadata query failed: {e}")
            raise ValueError(f"Failed to retrieve metadata from database: {e}") from e

        # Sort candidate tracks by similarity score descending
        enriched_candidates.sort(key=lambda x: x.similarity_score, reverse=True)
        
        logger.info(f"Retrieved and enriched {len(enriched_candidates)} candidate tracks.")
        if len(enriched_candidates) < 20:
            logger.warning(f"Sparse results warning: only {len(enriched_candidates)} candidates retrieved.")
            
        return enriched_candidates

    def _state_to_query_text(self, state: StateProfile) -> str:
        """
        Convert StateProfile to a natural language description matching the format 
        used during ingestion description generation.
        """
        # Primary & Secondary emotions
        emotions = state.primary_emotion
        if state.secondary_emotion:
            emotions += f", {state.secondary_emotion}"

        # Valence interpretation
        if state.valence < 0.3:
            mood_desc = "sad, melancholic, dark, and gloomy"
        elif state.valence < 0.6:
            mood_desc = "bittersweet, reflective, neutral, and nostalgic"
        else:
            mood_desc = "cheerful, happy, bright, and uplifting"

        # Energy interpretation
        if state.energy < 0.3:
            energy_desc = "calm, soft, peaceful, and low-energy"
        elif state.energy < 0.7:
            energy_desc = "moderate energy and pleasant"
        else:
            energy_desc = "high-energy, intense, loud, and active"

        # Acousticness
        acoustic_desc = "acoustic and organic" if state.acousticness > 0.5 else "electronic, electric, and synthesized"

        # Danceability
        dance_desc = "danceable, groovy, and rhythmic" if state.danceability > 0.6 else "subdued rhythm and steady"

        # Tempo Range / Description
        avg_tempo = sum(state.tempo_range) / len(state.tempo_range)
        if avg_tempo < 90:
            tempo_desc = "slow tempo"
        elif avg_tempo < 130:
            tempo_desc = "moderate tempo"
        else:
            tempo_desc = "fast tempo"

        # Instrumentalness
        instr_desc = "instrumental track" if state.instrumentalness > 0.5 else "vocal-heavy track"

        # Compile description
        query = (
            f"A {mood_desc} song representing {emotions}. "
            f"It features a {energy_desc} sound that is {acoustic_desc} with a {dance_desc} and {tempo_desc}. "
            f"It is an {instr_desc}."
        )
        return query
