import pytest
from app.pipeline.ranking_engine import RankingEngine
from app.models.emotion import EmotionalProfile, StateProfile, EmotionType
from app.models.track import CandidateTrack, Track

@pytest.fixture
def ranking_engine():
    return RankingEngine()

def test_compute_alignment(ranking_engine):
    target = StateProfile(
        primary_emotion="energetic",
        energy=0.9,
        valence=0.9,
        danceability=0.8,
        acousticness=0.1,
        instrumentalness=0.0,
        tempo_range=[120.0, 140.0]
    )

    # Perfect match track
    track_perfect = Track(
        id="t1", track_name="Perfect", artist="Artist A",
        valence=0.9, energy=0.9, danceability=0.8, tempo=130.0,
        acousticness=0.1, instrumentalness=0.0, loudness=-5.0,
        mode=1, duration_ms=180000, popularity=75
    )

    # Poor match track
    track_poor = Track(
        id="t2", track_name="Poor", artist="Artist B",
        valence=0.1, energy=0.1, danceability=0.2, tempo=70.0,
        acousticness=0.9, instrumentalness=0.8, loudness=-15.0,
        mode=0, duration_ms=210000, popularity=50
    )

    score_perfect = ranking_engine._compute_alignment(track_perfect, target)
    score_poor = ranking_engine._compute_alignment(track_poor, target)

    assert score_perfect > 0.95
    assert score_poor < 0.5

def test_compute_diversity(ranking_engine):
    # Setup some already selected tracks
    track_ref = Track(
        id="tr", track_name="Ref", artist="Artist X",
        valence=0.5, energy=0.5, danceability=0.5, tempo=120.0,
        acousticness=0.5, instrumentalness=0.0, loudness=-6.0,
        mode=1, duration_ms=200000, popularity=60
    )
    
    mock_selected = [
        MagicMockRankedTrack(track_ref)
    ]

    # Candidate with different artist
    track_diff = Track(
        id="t_diff", track_name="Diff", artist="Artist Y",
        valence=0.5, energy=0.5, danceability=0.5, tempo=120.0,
        acousticness=0.5, instrumentalness=0.0, loudness=-6.0,
        mode=1, duration_ms=200000, popularity=60
    )

    # Candidate with SAME artist as last track
    track_same = Track(
        id="t_same", track_name="Same", artist="Artist X",
        valence=0.5, energy=0.5, danceability=0.5, tempo=120.0,
        acousticness=0.5, instrumentalness=0.0, loudness=-6.0,
        mode=1, duration_ms=200000, popularity=60
    )

    div_diff = ranking_engine._compute_diversity(track_diff, mock_selected)
    div_same = ranking_engine._compute_diversity(track_same, mock_selected)

    assert div_diff == 1.0
    assert div_same == 0.0

def test_interpolate_target(ranking_engine):
    current = StateProfile(
        primary_emotion="sad", energy=0.2, valence=0.2, danceability=0.3,
        acousticness=0.7, instrumentalness=0.1, tempo_range=[70.0, 90.0]
    )
    desired = StateProfile(
        primary_emotion="happy", energy=0.8, valence=0.8, danceability=0.7,
        acousticness=0.3, instrumentalness=0.1, tempo_range=[110.0, 130.0]
    )

    # Interpolate at exactly the midpoint of a 3-track queue (index 1 / pos 2)
    mid_target = ranking_engine._interpolate_target(current, desired, 1, 3)

    assert pytest.approx(mid_target.energy) == 0.5
    assert pytest.approx(mid_target.valence) == 0.5
    assert pytest.approx(mid_target.danceability) == 0.5
    assert pytest.approx(mid_target.tempo_range[0]) == 90.0

class MagicMockRankedTrack:
    def __init__(self, track):
        self.track = track
