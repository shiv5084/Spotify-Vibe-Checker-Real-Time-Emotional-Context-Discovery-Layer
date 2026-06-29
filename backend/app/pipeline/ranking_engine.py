import logging
from typing import List, Optional
from app.models.emotion import EmotionalProfile, StateProfile
from app.models.track import CandidateTrack, RankedTrack, Track

logger = logging.getLogger(__name__)

class RankingEngine:
    def __init__(self):
        # Weights matching implementation_plan.md
        self.w_similarity = 0.25
        self.w_alignment = 0.45
        self.w_diversity = 0.15
        self.w_arc = 0.15

    def rank(self, candidates: List[CandidateTrack], profile: EmotionalProfile, queue_size: int = 12) -> List[RankedTrack]:
        """
        Rank and order candidate tracks based on emotional alignment, semantic similarity,
        artist/genre diversity, and emotional transition arc.
        
        Args:
            candidates: List of retrieved CandidateTracks.
            profile: Emotional profile containing target states.
            queue_size: Number of tracks to select and sequence.
            
        Returns:
            List of RankedTracks ordered by position.
        """
        logger.info(f"Ranking {len(candidates)} candidates for queue size: {queue_size}")
        
        if not candidates:
            return []

        # Determine target state for overall alignment (desired state takes precedence)
        overall_target = profile.desired if profile.desired else profile.current
        
        pool = list(candidates)
        selected_tracks: List[RankedTrack] = []

        # Sequential greedy assignment to build the queue
        for pos in range(queue_size):
            if not pool:
                break
                
            # 1. Determine interpolated target for the current position (emotional arc)
            pos_target = self._interpolate_target(profile.current, profile.desired, pos, queue_size)
            
            best_cand = None
            best_comp_score = -999.0
            best_scores = {}

            for cand in pool:
                track = cand.track
                
                # A. Similarity Score (already computed by Qdrant/vector search)
                sim_score = cand.similarity_score

                # B. Overall Emotional Alignment Score
                align_score = self._compute_alignment(track, overall_target)

                # C. Positional Arc Score (alignment against current position's target)
                arc_score = self._compute_alignment(track, pos_target)

                # D. Diversity Score
                div_score = self._compute_diversity(track, selected_tracks)

                # E. Composite Score
                comp_score = (
                    self.w_similarity * sim_score +
                    self.w_alignment * align_score +
                    self.w_diversity * div_score +
                    self.w_arc * arc_score
                )

                if comp_score > best_comp_score:
                    best_comp_score = comp_score
                    best_cand = cand
                    best_scores = {
                        "similarity": sim_score,
                        "alignment": align_score,
                        "diversity": div_score,
                        "arc": arc_score,
                        "composite": comp_score
                    }

            if best_cand:
                # Remove selected candidate from the pool
                pool.remove(best_cand)
                
                # Append to selected queue
                selected_tracks.append(RankedTrack(
                    track=best_cand.track,
                    similarity_score=best_scores["similarity"],
                    alignment_score=best_scores["alignment"],
                    diversity_score=best_scores["diversity"],
                    arc_score=best_scores["arc"],
                    composite_score=best_scores["composite"],
                    position=pos + 1
                ))

        logger.info(f"Successfully selected and sequenced {len(selected_tracks)} tracks.")
        return selected_tracks

    def _compute_alignment(self, track: Track, target: StateProfile) -> float:
        """
        Compute how well a track's audio features match a target StateProfile.
        Returns a score between 0.0 and 1.0 (1.0 being perfect match).
        """
        # Normalize tempos to 0.0-1.0 range (capping at 200 BPM)
        track_tempo_norm = min(track.tempo / 200.0, 1.0)
        target_tempo_mid = sum(target.tempo_range) / len(target.tempo_range)
        target_tempo_norm = min(target_tempo_mid / 200.0, 1.0)

        # Distances
        d_valence = abs(track.valence - target.valence)
        d_energy = abs(track.energy - target.energy)
        d_dance = abs(track.danceability - target.danceability)
        d_acoustic = abs(track.acousticness - target.acousticness)
        d_tempo = abs(track_tempo_norm - target_tempo_norm)

        # Weighted distance average
        weighted_dist = (
            0.35 * d_valence +
            0.25 * d_energy +
            0.15 * d_dance +
            0.15 * d_acoustic +
            0.10 * d_tempo
        )

        return max(0.0, 1.0 - weighted_dist)

    def _compute_diversity(self, track: Track, selected: List[RankedTrack]) -> float:
        """
        Calculate a diversity score based on artist repetition in recent selections.
        Returns 1.0 (fully diverse), 0.5 (artist selected 2 tracks ago), or 0.0 (artist selected in previous track).
        """
        if not selected:
            return 1.0
            
        # Get artist names
        current_artist = track.artist.strip().lower()
        
        # Check 1 position ago
        if selected[-1].track.artist.strip().lower() == current_artist:
            return 0.0
            
        # Check 2 positions ago
        if len(selected) > 1 and selected[-2].track.artist.strip().lower() == current_artist:
            return 0.5
            
        return 1.0

    def _interpolate_target(self, current: StateProfile, desired: Optional[StateProfile], pos: int, total: int) -> StateProfile:
        """
        Interpolate audio features between current and desired state profiles for a given queue position.
        """
        if not desired or total <= 1:
            return current

        # Calculate transition fraction
        fraction = pos / (total - 1)

        # Linear interpolation
        valence = (1 - fraction) * current.valence + fraction * desired.valence
        energy = (1 - fraction) * current.energy + fraction * desired.energy
        dance = (1 - fraction) * current.danceability + fraction * desired.danceability
        acoustic = (1 - fraction) * current.acousticness + fraction * desired.acousticness
        
        # Interpolate tempo ranges
        tempo_min = (1 - fraction) * current.tempo_range[0] + fraction * desired.tempo_range[0]
        tempo_max = (1 - fraction) * current.tempo_range[1] + fraction * desired.tempo_range[1]

        # Use transition type for descriptive name mapping
        primary = current.primary_emotion if fraction < 0.5 else desired.primary_emotion
        secondary = current.secondary_emotion if fraction < 0.5 else desired.secondary_emotion

        return StateProfile(
            primary_emotion=primary,
            secondary_emotion=secondary,
            energy=energy,
            valence=valence,
            danceability=dance,
            acousticness=acoustic,
            instrumentalness=(1 - fraction) * current.instrumentalness + fraction * desired.instrumentalness,
            tempo_range=[tempo_min, tempo_max]
        )
