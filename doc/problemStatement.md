# Vibe-Checker — Real-Time Emotional Context Discovery Layer

## Problem Statement

---

## 1. Business Problem

Spotify operates one of the world's most sophisticated music recommendation systems, yet a disproportionate share of listening still gravitates toward familiar artists, repeat playlists, and previously discovered tracks. This pattern limits **meaningful music discovery** and gradually erodes **long-term user engagement**.

While Spotify excels at modeling *historical* listening behavior, it has a critical blind spot: it cannot understand **why** a user wants music *right now*. As a result, many listening sessions begin without sufficient emotional context — leaving the system to guess based on past patterns rather than present needs.

> **The Gap:** Spotify knows *what* you've listened to. It doesn't know *what you need* in this moment.

---

## 2. Product Problem

Spotify's recommendation engine is optimized around **retrospective signals** — what users have played before, what similar users enjoy, and what's trending. These are powerful for surfacing familiar content, but they fail when users arrive with a **real-time emotional intent**.

### The User Experience Breakdown

When a user has a specific emotional need — such as *"I need something that slowly lifts my mood"* or *"melancholy but hopeful"* — the current experience forces them to:

- Search by keywords (which map poorly to emotions)
- Browse multiple curated playlists (which are generic, not personalized)
- Skip tracks repeatedly (frustrating trial-and-error)
- Abandon discovery altogether (defaulting to familiar music)

### Why Current Recommendations Fall Short

Today's recommendation systems are primarily driven by:

| Signal Type              | What It Captures                     | What It Misses                          |
|--------------------------|--------------------------------------|-----------------------------------------|
| Historical behavior      | Long-term taste patterns             | Current emotional state                 |
| Collaborative filtering  | What similar users like              | Individual real-time intent             |
| Audio similarity         | Sonic characteristics of tracks      | Emotional meaning and nuance            |
| Popularity / engagement  | What's trending or frequently played | Personal emotional needs in the moment  |

> **Core Insight:** These approaches infer *what users usually like*, but cannot understand *what users need right now*. This creates a persistent gap between a user's emotional intent and the music surfaced by existing algorithms — leading to repetitive listening, reduced discovery, and lower session satisfaction.

---

## 3. Why AI Is Required

Understanding free-form emotional language is an **open-ended natural language reasoning problem** — not a rules-based classification task.

The same emotional need can be expressed in countless ways:

| User Input                                         | Underlying Intent                                |
|----------------------------------------------------|--------------------------------------------------|
| *"Need something that heals slowly"*               | Gradual emotional recovery, gentle energy        |
| *"I feel empty but hopeful"*                       | Low current state, desire for upward transition  |
| *"Music that feels like rain after a difficult day"* | Cathartic calm, bittersweet comfort              |
| *"Quiet confidence"*                               | Subdued energy with positive self-assurance      |

These inputs **cannot** realistically be captured through:
- Predefined mood categories (too rigid)
- Keyword matching (too literal)
- Collaborative filtering (too backward-looking)

### What Large Language Models Uniquely Enable

| Capability                          | Description                                                                 |
|-------------------------------------|-----------------------------------------------------------------------------|
| Emotional language interpretation   | Parse nuanced, metaphorical, and ambiguous emotional expressions            |
| Latent intent extraction            | Identify both the *current* emotional state and the *desired* emotional state |
| Acoustic–mood mapping               | Translate extracted intent into audio feature vectors (energy, valence, tempo) |
| Real-time queue generation          | Produce a ranked, emotionally coherent listening queue instantly             |

> **Without LLM reasoning**, the system cannot reliably translate natural language emotions into structured signals for personalized music discovery.

---

## 4. MVP Goal

Build an **AI-powered emotional intent understanding layer** that enables users to describe how they feel in natural language and instantly receive an **emotionally matched Vibe Queue** — before playback begins.

The MVP should demonstrate that **LLM-driven emotional understanding improves music discovery** beyond what traditional recommendation methods can achieve.

### Example Prompts → Vibe Queue

| User Prompt                                  | Expected System Behavior                                      |
|----------------------------------------------|---------------------------------------------------------------|
| *"Feeling low, need something that lifts me slowly"* | Gradual energy curve: start mellow, build to uplifting         |
| *"Melancholy but hopeful"*                   | Bittersweet tracks with positive undercurrents                 |
| *"Peaceful after a long day"*                | Low-energy, high-warmth ambient / acoustic                     |
| *"Angry but want to calm down"*              | Descending energy arc: intense start, gentle resolution        |

**Flow:** The system converts the prompt into structured emotional signals via LLM inference, retrieves semantically matched tracks via vector search, and ranks them into an emotionally coherent Vibe Queue.

---

## 5. Success Criteria

The MVP should demonstrate that natural-language emotional input can:

| Metric                            | Target Outcome                                                        |
|-----------------------------------|-----------------------------------------------------------------------|
| **Reduced browsing before playback** | Users start listening faster compared to manual search/browse         |
| **Increased meaningful discovery**   | Users encounter tracks outside their usual listening patterns         |
| **Improved perceived relevance**     | Users rate the Vibe Queue as emotionally aligned with their prompt    |
| **AI capability validation**         | Demonstrate capabilities unavailable through traditional recommendation systems |

---

## 6. Project Scope

### 6.1 In Scope

#### User Experience
- Persistent **Vibe Checker** input on the Home page
- Free-text emotional prompt input
- Generate **one Vibe Queue per prompt**
- Queue displayed before playback begins

#### Music Retrieval
- Semantic vector search over track embeddings
- Emotion-aware ranking engine
- Top-N queue generation
- Spotify dataset indexing with metadata filtering

#### Authentication
- Google OAuth integration
- User session management

#### Infrastructure
- REST API backend
- Redis caching layer
- Vector database: **Qdrant Cloud** (free tier)
- PostgreSQL metadata store: **Supabase**

---

### 6.2 Out of Scope

The MVP intentionally focuses **only on emotional context expressed through language**. The following capabilities are explicitly excluded:

#### Situational Context
No understanding of real-world situations:
> Driving home · Commuting · Studying · Working late · Cooking · Traveling · Rainy day · Vacation

#### Activity Context
No activity detection:
> Running · Gym · Coding · Reading · Sleeping · Walking

#### Environmental Signals
No use of external sensor or device data:
> GPS · Weather · Calendar · Time of day · Wearable sensors · Phone sensors · Motion · Heart rate · Ambient sound · Microphone

#### Long-Term Emotional Intelligence
Not included in MVP:
> Emotional memory · Emotional profile · Mood history · Adaptive emotional learning

#### Emotional Arc Generation
- No multi-stage emotional journeys
- Only lightweight **Current → Target** progression is supported:

```
Lonely  →  Hopeful
(gradual transition)
```

- No dynamic playlist evolution during playback

#### Feedback Learning
No feedback loop mechanisms:
> Thumbs up/down · Reinforcement learning · Online personalization · Queue refinement · Preference adaptation

Each prompt is processed **independently** — no cross-session learning.

#### Conversational AI
No dialogue capabilities:
> Follow-up dialogue · Clarifying questions · Chatbot · Multi-turn conversation

**One prompt → One queue.** Single-turn interaction only.

#### Spotify Production Integration
The MVP will **not** integrate with Spotify's production recommendation engine, playback APIs, or user listening history. It operates independently using a public Spotify tracks dataset to validate the concept.

---

## 7. Tech Stack

| Component                | Technology                          | Purpose                                    |
|--------------------------|-------------------------------------|--------------------------------------------|
| **LLM**                 | Groq — Llama-3.1-8B-Instant        | Emotion and intent extraction from prompts |
| **Embedding Model**     | BAAI/bge-small-en-v1.5             | Semantic retrieval via track embeddings    |
| **Vector Database**     | Qdrant Cloud (Free Tier)            | Low memory, high-efficiency vector search  |
| **Metadata Database**   | Supabase (PostgreSQL)               | Track metadata storage + Google OAuth      |
| **Cache**               | Redis                               | Response and session caching               |
| **Music Search**        | Vector Similarity + Custom Ranking  | Emotion-aware track retrieval and ordering |
| **Dataset**             | [Spotify Tracks Dataset (HuggingFace)](https://huggingface.co/datasets/maharshipandya/spotify-tracks-dataset) | Public dataset for MVP validation |

---

## 8. Emotion Understanding

### Supported Metadata

All audio features and metadata available in the [Spotify Tracks Dataset](https://huggingface.co/datasets/maharshipandya/spotify-tracks-dataset) are supported for emotion mapping and retrieval, including but not limited to: `valence`, `energy`, `danceability`, `tempo`, `acousticness`, `instrumentalness`, `loudness`, `speechiness`, `liveness`, and `mode`.

### Emotion Type Classification

The LLM must classify the type of emotional expression in each prompt:

| Mood Prompt | Emotion Type | Classification |
|---|---|---|
| *"Feeling lonely but optimistic"* | **Mixed emotion** | `mixed_emotion` — two concurrent emotions in current state |
| *"Feeling low, need something that lifts me slowly"* | **Current + desired emotional outcome** | `current_with_desired` — current state + target state expressed |
| *"Give me something nostalgic"* | **Desired emotion** | `desired_only` — only target mood specified |
| *"I feel emotionally exhausted"* | **Current emotion** | `current_only` — only current state expressed |

### Sample LLM Emotion Extraction Response

```json
{
  "emotion_type": "mixed_emotion | current_with_desired | desired_only | current_only",
  "current_state": {
    "primary_emotion": "lonely",
    "secondary_emotion": "optimistic",
    "energy": "low_medium",
    "valence": 0.45
  },
  "desired_state": {
    "primary_emotion": "hopeful",
    "secondary_emotion": null,
    "energy": "medium",
    "valence": 0.65
  },
  "transition": {
    "type": "maintain | gradual | immediate"
  },
  "confidence": 0.0
}
```

> [!NOTE]
> - `emotion_type` classifies the user's emotional expression pattern for downstream ranking and queue assembly logic.
> - Both `current_state` and `desired_state` support `primary_emotion` and `secondary_emotion` (secondary can be `null` if only one emotion is expressed).
> - When `emotion_type` is `desired_only`, the system infers a neutral current state. When `current_only`, the system infers that the desired state matches the current state (maintain transition).

> [!NOTE]
> The LLM extraction schema should map to **all relevant metadata fields** available in the Spotify dataset to maximize retrieval precision during vector search and ranking.

---