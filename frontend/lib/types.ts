export interface StateProfile {
  primary_emotion: string;
  secondary_emotion: string | null;
  energy: number;
  valence: number;
  danceability: number;
  acousticness: number;
  instrumentalness: number;
  tempo_range: [number, number];
}

export interface EmotionalProfile {
  emotion_type: string;
  current: StateProfile;
  desired: StateProfile | null;
  transition: string;
  confidence: number;
}

export interface Track {
  id: string;
  track_name: string;
  artist: string;
  album: string;
  valence: number;
  energy: number;
  danceability: number;
  tempo: number;
  acousticness: number;
  instrumentalness: number;
  loudness: number;
  speechiness: number;
  liveness: number;
  mode: number;
  duration_ms: number;
  popularity: number;
  track_genre: string;
  embedding_text: string;
}

export interface RankedTrack {
  track: Track;
  similarity_score: number;
  alignment_score: number;
  diversity_score: number;
  arc_score: number;
  composite_score: number;
  position: number;
}

export interface VibeQueue {
  prompt: string;
  emotion_type: string;
  emotional_profile: EmotionalProfile;
  confidence: number;
  tracks: RankedTrack[];
  queue_size: number;
  ai_explanation: string | null;
  generated_at: string;
}

export interface UserProfile {
  id: string;
  email: string;
  display_name: string;
  avatar_url: string | null;
}
