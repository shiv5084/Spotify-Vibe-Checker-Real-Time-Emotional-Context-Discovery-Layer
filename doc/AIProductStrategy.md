**AI PRD & Product Strategy Document**
**AI-Powered Product Specification & System Design Blueprint**
# Vibe-Checker — Real-Time Emotional Context Discovery Layer — Product Strategy

Welcome to the Vibe-Checker AI Design Workspace. As an **AI Product Manager**, the goal of this project is to design, model, and build an AI-powered emotional intent understanding layer that translates natural-language emotional prompts into personalized, emotionally coherent music discovery queues — instantly, before playback begins.

We are approaching this design step-by-step, ensuring absolute alignment with product principles (Emotional Accuracy, Discovery Quality, Low Latency, Retrieval Precision, User Trust, Simplicity) and robust engineering practices.

> **Author:** Shiv
> **Date:** 2026-06-28
> **Status:** In Progress
> **Related Docs:** [problemStatement.md](problemStatement.md)

---

## 🗺️ Project Design Roadmap

- [ ] **Step 1: Defining the Problem Statement**
- [ ] **Step 2: Mapping the User Journey & Defining System Touchpoints**
- [ ] **Step 3: The System's Job Description**

---

## 📌 Step 1: Defining the Problem Statement

Before we touch system design, we need crisp clarity on what we're actually solving. Building AI pipelines without clear boundaries and baselines leads to solving the wrong problem.

### 1.1 Frame the Current State (No Solution Language Yet)

We define the problem in direct user and business terms using the standard PM template:

> **Template:**
> `[User segment] currently [current behavior] when [trigger]. This causes [pain for user] and [cost for business]. Today we solve this by [existing solution] which fails because [gaps].`

#### Applied to the Vibe-Checker Emotional Discovery System:

**Music listeners and emotional seekers** currently **manually search for mood-matching music by browsing curated playlists, using keyword search, skipping through tracks, or defaulting to familiar music** when **they arrive on Spotify with a specific emotional need — such as "I need something that slowly lifts my mood" or "melancholy but hopeful"**. This causes **user frustration due to repeated skipping, inability to express emotions as search queries, reliance on generic mood playlists that don't match individual emotional nuance, and ultimately abandoning music discovery in favor of replaying known tracks**, and **leads to reduced meaningful discovery, lower long-term engagement, stagnant listening patterns, and missed opportunities for deeper emotional connection between listeners and Spotify's vast catalogue**. Today, we solve this by **relying on users to manually search keywords, browse mood-tagged playlists (e.g., "Sad Songs," "Happy Hits"), use Spotify's Discover Weekly or Daily Mix algorithms, or skip through tracks until something feels right**, which fails because **keyword search maps poorly to emotions, curated playlists are generic and not personalized to individual emotional nuance, recommendation algorithms are optimized for historical behavior rather than real-time emotional intent, and no existing system can interpret natural-language emotional expressions like "music that feels like rain after a difficult day."**

---

### 1.2 Quantifying the Problem (The PM's Job)

To measure success and prove value, we establish our performance baselines prior to system design:

| Metric | Baseline (Today's Manual Discovery) | Target (v1 Vibe-Checker) | Source / Rationale |
| :--- | :--- | :--- | :--- |
| **Time to First Relevant Track** | **2–10 minutes** (browse + skip loop) | **< 10 seconds** (prompt → Vibe Queue) | Eliminates manual search via LLM-driven queue generation |
| **Number of Skips Before Satisfaction** | **5–15 skips** per session | **0–2 skips** per Vibe Queue | Emotionally matched tracks reduce trial-and-error |
| **Discovery Rate (New Artists/Tracks)** | **< 15%** of listening is new music | **> 50%** of Vibe Queue tracks are new to user | Semantic search surfaces unfamiliar but emotionally aligned music |
| **Emotional Alignment Accuracy** | **0%** (no emotional understanding) | **≥ 75%** perceived emotional match | User rates queue alignment with emotional prompt |
| **Input Expressiveness** | **Keywords only** (search bar) | **Free-form natural language** | LLM interprets metaphorical, nuanced, and ambiguous emotional input |
| **Playlist Personalization** | **Generic** (mood tags, collaborative filtering) | **100% prompt-specific** | Every queue is uniquely generated for the specific emotional input |
| **Queue Generation Latency** | **N/A** (no automated queue) | **< 5 seconds** (end-to-end pipeline) | LLM inference + vector search + ranking complete under latency target |
| **Session Abandonment Rate** | **~30–40%** (complex emotional searches) | **< 10%** | Instant gratification from Vibe Queue reduces abandonment |

---

### 1.3 Scoping the Problem — What's IN vs. OUT

To prevent scope creep and establish a clean boundary for our v1 system, we explicitly outline what the system will and will not handle.

> [!NOTE]
> *Why this matters for AI systems:* Every "out of scope" item is an explicit boundary condition — either filtered at the input layer or simply not processed. Naming them now prevents prompt degradation, model overreach, and scope overflow.

*   **In Scope (v1 — Target Flows):**
    *   **Natural-Language Input:** Free-text emotional prompts entered via the Home page Vibe Checker input.
    *   **Emotion Extraction:** LLM-powered extraction of current emotional state, desired emotional state, and transition type from user prompt.
    *   **Semantic Retrieval:** Vector similarity search over pre-indexed Spotify track embeddings using BAAI/bge-small-en-v1.5.
    *   **Emotion-Aware Ranking:** Custom ranking engine that combines vector similarity scores with audio feature alignment (valence, energy, tempo, danceability, acousticness).
    *   **Vibe Queue Generation:** Top-N emotionally matched tracks assembled into a coherent Vibe Queue with emotional arc (current → desired state).
    *   **Queue Display:** Vibe Queue displayed on-screen before playback begins, allowing user to review the queue.
    *   **Authentication:** Google OAuth via Supabase for user session management.
    *   **Caching:** Redis caching for repeated or similar prompts to reduce latency and API costs.
    *   **Dataset Indexing:** One-time ingestion and embedding of the public Spotify Tracks Dataset into Qdrant vector database.

*   **Out of Scope (Explicit Boundaries):**
    *   **Situational Context:** No understanding of real-world situations (driving, commuting, studying, working late, cooking, traveling, rainy day, vacation).
    *   **Activity Context:** No activity detection (running, gym, coding, reading, sleeping, walking).
    *   **Environmental Signals:** No use of GPS, weather, calendar, time of day, wearable sensors, phone sensors, motion, heart rate, ambient sound, or microphone data.
    *   **Long-Term Emotional Intelligence:** No emotional memory, emotional profile, mood history, or adaptive emotional learning across sessions.
    *   **Multi-Stage Emotional Arcs:** No dynamic playlist evolution during playback. Only lightweight Current → Target progression at queue generation time.
    *   **Feedback Learning:** No thumbs up/down, reinforcement learning, online personalization, queue refinement, or preference adaptation. Each prompt is processed independently.
    *   **Conversational AI:** No follow-up dialogue, clarifying questions, chatbot, or multi-turn conversation. One prompt → One queue.
    *   **Spotify Production Integration:** No integration with Spotify's production APIs, playback controls, or user listening history. Operates independently using a public dataset.
    *   **Voice Input:** No speech-to-text or voice-first interaction (text-only in v1).
    *   **Actual Audio Playback:** No embedded music player or streaming integration. Queue is informational.
    *   **Social Features:** No sharing queues, collaborative vibing, or social media integration.
    *   **Multi-Language Support:** English-only in v1.

---

### 1.4 Define Success Metrics

Our success definition spans three operational dimensions:

1.  **User Outcome (Listener):** *"I type how I feel in natural language, and within seconds I see a Vibe Queue of tracks that genuinely match my emotional state. The tracks surface music I wouldn't have found through normal search or browse. I feel understood — the system gets my vibe."*

2.  **Business Outcome (Platform / Concept Validation):** *"The system demonstrates that LLM-driven emotional understanding produces measurably better music discovery than keyword search, mood playlists, or collaborative filtering alone. Users engage with more diverse music, spend less time browsing, and rate Vibe Queue results as emotionally relevant — validating the concept for potential integration into a production music platform."*

3.  **AI Pipeline Outcome (System Engineering):** *"The AI pipeline completes end-to-end — prompt → LLM extraction → vector search → ranking → queue — with ≥ 95% success rate and < 5 second latency. The LLM accurately extracts emotional intent with ≥ 80% alignment to user's perceived emotion. The vector search retrieves semantically relevant tracks, and the ranking engine produces emotionally coherent queue ordering. All pipeline stages are logged for observability and debugging."*

---

### 1.5 The "Why AI?" Gut Check

Before building, we verify why a standard mood playlist, keyword search, or genre filter is insufficient, and why an **LLM-Powered Emotional Understanding Pipeline** is strictly required:

1.  **Unbounded Emotional Language:**
    *   *Problem:* Human emotional expression is infinite in variety. Users describe feelings using metaphors, contradictions, compound emotions, and culturally specific references that cannot be enumerated in advance.
    *   *Example:* *"Music that feels like rain after a difficult day"*
    *   *Keyword Search:* ❌ Fails — no keyword maps to "cathartic calm with bittersweet comfort."
    *   *Mood Playlist:* ❌ Fails — "Rainy Day" playlists are generic and miss the "after a difficult day" emotional nuance.
    *   *LLM Pipeline:* ✅ Succeeds — LLM interprets the metaphorical language, extracts latent emotions (catharsis, melancholy, gentle recovery), maps to audio features (low energy, medium valence, high acousticness), and retrieves emotionally aligned tracks.

2.  **Dual-State Emotional Understanding:**
    *   *Key Distinction:* Users don't just describe how they feel — they describe where they *want* to go. "Angry but want to calm down" implies a current state (anger, high energy) and a desired state (calm, low energy) with a gradual transition.
    *   *No existing system* captures this dual-state intent. Mood playlists are single-state ("Calm," "Angry"). LLMs can extract both states and model the transition arc.

3.  **Semantic Gap Between Emotions and Audio Features:**
    *   *Problem:* Spotify tracks have numerical audio features (valence: 0.0–1.0, energy: 0.0–1.0, tempo, danceability, etc.) but no semantic emotional labels. The system must bridge the gap between "lonely but optimistic" and `{valence: 0.45, energy: 0.35, acousticness: 0.7}`.
    *   *Rule-Based Approach:* ❌ Fails — emotions don't map 1:1 to audio features. "Quiet confidence" has different audio feature requirements than "peaceful after a long day," even though both are low-energy.
    *   *LLM Pipeline:* ✅ Succeeds — LLM generates nuanced, context-dependent mappings. Combined with semantic embeddings, the system bridges emotion-to-audio space dynamically.

4.  **Emotional Coherence in Queue Ordering:**
    *   *Problem:* Even if individual tracks match the emotion, a randomly ordered queue breaks the emotional experience. A queue for "feeling low, need something that lifts me slowly" must start somber and gradually build — track order matters.
    *   *Collaborative Filtering:* ❌ Fails — optimizes for similarity, not emotional arc.
    *   *LLM + Ranking Engine:* ✅ Succeeds — the ranking engine uses the extracted Current → Target transition to order tracks along an emotional gradient.

5.  **Personalization Without History:**
    *   *Key Distinction:* Unlike traditional recommendation systems that require extensive listening history, Vibe-Checker provides instant personalization based on a single prompt. No cold-start problem — every user gets a relevant queue from their first interaction.

---

### 💬 PM Alignment: Key Design Questions for Step 1

To finalise Step 1, please provide feedback on these key baseline assumptions:

1. **Target Latency:** Tiered latency targets:
   - **< 1 sec** → UI acknowledges input (loading state begins)
   - **< 3 sec** → LLM emotion extraction complete (emotional profile shown)
   - **< 5 sec** → full Vibe Queue generated and displayed
2. **Queue Size:** **10–15 tracks** per Vibe Queue (default)
3. **Emotional Extraction Depth:** Extract current state, desired state, and transition type. Map to all available Spotify audio features.
4. **Prompt Caching:** Cache identical or near-identical prompts for **24 hours** via Redis to reduce LLM calls.

> **Step 1 Status:** ⏳ **AWAITING PM FEEDBACK**

---

## 📌 Step 2: Mapping the User Journey & Defining System Touchpoints

This is where most PMs jump straight to "the pipeline will do X." Wrong. First map the **human journey as it exists today**, then decide exactly where the AI shows up. The journey reveals the system's job — not the other way around.

---

### 2.1 Map the Current-State Journey (No AI Yet)

Pick one flow at a time. Vibe-Checker addresses one primary flow: **the emotional music discovery cycle**. Map it from the moment a user feels an emotional need for music to the moment they're listening to something that matches.

**Current-state journey: Emotional Music Discovery (Manual):**

| # | Step | User Does | System / Tool Involved | Pain Points | Time Spent |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | **Emotional Trigger** | Feels a specific emotion or mood shift: *"I feel melancholy but hopeful"* | None — internal emotional state | No structured way to translate emotion into music search; user must self-translate to keywords | 0 min |
| 2 | **Keyword Translation** | Mentally converts emotion to search terms: types "sad songs" or "uplifting music" | Spotify search bar | Lossy translation — "melancholy but hopeful" becomes flat "sad" or "happy"; nuance is lost | 1–2 min |
| 3 | **Playlist Browsing** | Scrolls through Spotify's curated mood playlists: "Sad Songs," "Mood Booster," "Peaceful Piano" | Spotify Browse page | Playlists are generic, not personalized; "Sad Songs" is a single mood, not "melancholy but hopeful"; dozens of playlists to browse | 3–5 min |
| 4 | **Track Sampling** | Plays preview of tracks, skips repeatedly if they don't match the felt emotion | Spotify playback | Trial-and-error is slow and frustrating; 5–15 skips before finding a match; emotional momentum is broken | 3–8 min |
| 5 | **Discovery Attempt** | Tries "Discover Weekly" or "Daily Mix" — but these are based on listening history, not current emotion | Spotify recommendation engine | Recommendations are backward-looking; irrelevant to current emotional state; no way to steer by emotion | 2–5 min |
| 6 | **Compromise or Abandon** | Settles for a "close enough" track or gives up and replays familiar music | Familiar library / saved songs | Discovery fails; user retreats to comfort zone; emotional need unmet or only partially met | 1–3 min |

> [!NOTE]
> **Total Time:** 10–20+ minutes of fragmented browsing, with most sessions ending in compromise or abandonment. Steps 2–4 represent the core pain — the **emotion-to-music translation gap** — where users lose nuance and momentum.

---

### 2.2 Identify the "AI-Shaped" Steps

Now overlay where the AI uniquely adds value. Not every step is AI territory. Use this filter:

| Question | If Yes → |
| :--- | :--- |
| Does it require understanding messy, unstructured input? | **AI (LLM)** |
| Does it require mapping between semantic and numerical spaces? | **AI (Embedding + Ranking)** |
| Does it require judgment within a defined rule set? | **AI (with guardrails)** |
| Does it require human creativity or subjective choice? | **Human** |
| Is it a deterministic data movement step (index dataset, filter metadata)? | **Script / Pipeline — not AI** |

**Applied to the Vibe-Checker pipeline:**

| Step | AI? | Why | System Component |
| :--- | :--- | :--- | :--- |
| 1. Emotional Trigger | **No — user provides** | User initiates with free-text prompt; system receives as input | User input → Vibe Checker UI |
| 2. Keyword Translation | **AI — eliminates this step entirely** | LLM replaces manual keyword translation; user types raw emotion, LLM extracts structured intent | Emotion Extraction Engine (LLM) |
| 3. Playlist Browsing | **AI — replaces manual browsing** | Semantic vector search surfaces tracks by emotional meaning, not keywords or mood tags | Semantic Retrieval Engine (Qdrant) |
| 4. Track Sampling | **AI — drastically reduces skipping** | Emotion-aware ranking ensures track relevance and emotional arc coherence before playback | Ranking Engine |
| 5. Discovery Attempt | **AI — core value** | Vector search surfaces emotionally relevant tracks regardless of listening history — no cold-start, no backward-looking bias | Semantic Retrieval + Ranking |
| 6. Compromise/Abandon | **AI — prevents this outcome** | High-relevance Vibe Queue means users get emotionally matched music immediately; no need to compromise | End-to-end pipeline output |

> [!NOTE]
> **Steps 2–5 are where the AI earns its keep.** The LLM eliminates the lossy keyword translation. Vector search replaces manual browsing. The ranking engine replaces trial-and-error skipping. Together, they collapse 10–20 minutes of fragmented discovery into < 5 seconds.

---

### 2.3 Define System Touchpoints (Triggers + Entry Surfaces)

Where and how does the pipeline actually start? The trigger mechanism is a design choice that affects reliability, latency, and user experience.

| Touchpoint | How It Works | Pros | Cons | Recommendation |
| :--- | :--- | :--- | :--- | :--- |
| **Web App (Home Page — Vibe Checker Input)** | User types emotional prompt into persistent input field on Home page; REST API triggers AI pipeline | Natural interaction; always visible; zero friction; accessible from any browser | Requires internet; limited to text input in v1 | ✅ **Primary — Start here (v1)** |
| **Mobile Web (Responsive)** | Same as web app but accessed via mobile browser; responsive layout | Reaches mobile users without native app | Smaller input area; typing on mobile less natural for long prompts | ✅ **v1 — Responsive design** |
| **Voice Input** | User speaks emotional prompt; speech-to-text converts to text; same pipeline | More natural for emotional expression; hands-free | Requires STT integration; higher latency; transcription errors | 🔲 **v2 — Future** |
| **API Integration** | Third-party apps call REST API with emotional prompt | Enables partnerships; embed Vibe-Checker in other apps | Requires API key management; authentication | 🔲 **v2 — Future** |
| **Browser Extension** | Overlay on Spotify Web Player; user types emotion while browsing | Context-rich; meets user where they already are | Requires extension development; Spotify policy compliance | 🔲 **v3 — Future** |

> [!NOTE]
> **Pick one primary touchpoint for v1.** The web app with a persistent Vibe Checker input on the Home page is the correct default — it provides the most direct interaction model. Responsive design ensures mobile access. Voice and integrations can follow in v2.

---

### 2.4 Define the Handoff Design (This Is Critical)

Every AI pipeline needs **three exits mapped from day one**. For an emotional music discovery system, "handoff" means: what happens when the system can't generate a meaningful Vibe Queue?

**Exit 1 — Happy Path (Pipeline Completes Successfully):**
- User enters emotional prompt
- LLM extracts emotional profile with high confidence (≥ 0.7)
- Vector search returns sufficient candidate tracks (≥ 20)
- Ranking engine produces coherent Vibe Queue (10–15 tracks)
- Queue displayed to user with emotional summary
- **User role:** Review queue, begin listening, or enter a new prompt

**Exit 2 — Soft Failure (Low Confidence or Sparse Results):**
- LLM extracts emotional profile but with low confidence (< 0.7)
- Vector search returns fewer candidates than expected (< 20 but ≥ 5)
- System still generates Vibe Queue but with warning: *"We interpreted your vibe as [X]. Refine your prompt for better results."*
- Queue may be shorter (5–10 tracks)
- **User role:** Accept queue, or refine prompt and try again

**Exit 3 — Hard Failure (Extraction Fails or No Results):**
- LLM cannot extract meaningful emotional intent (nonsensical input, empty prompt, adversarial content)
- Vector search returns < 5 candidate tracks (extremely niche or contradictory emotion)
- System shows clear error: *"We couldn't understand that vibe. Try describing how you feel — like 'peaceful after a long day' or 'melancholy but hopeful.'"*
- Suggests example prompts to guide user
- **User role:** Re-enter prompt with clearer emotional language

**System Guardrails (Always Active):**

| Guardrail | Effect |
| :--- | :--- |
| **Input sanitization** | Strip HTML, limit prompt length (500 chars max), block injection attempts |
| **Content filtering** | Flag or reject prompts with harmful, violent, or explicit emotional content |
| **Confidence threshold** | LLM returns confidence score; low confidence triggers soft failure path |
| **Minimum results threshold** | If vector search returns < 5 tracks, trigger hard failure instead of empty queue |
| **Rate limiting** | Max 20 prompts per user per hour to prevent abuse and manage API costs |
| **Cache-first** | Check Redis cache before LLM call; serve cached queue for identical prompts |

> [!IMPORTANT]
> **PM Rule:** If a user cannot understand why their Vibe Queue doesn't match their emotion, the feedback loop is insufficient. The system must always show the extracted emotional profile (current state → desired state) so users can see *how* their input was interpreted and adjust accordingly.

---

### 2.5 Define the Future-State Journey (With AI)

Now redraw the journey with the AI in place. This is the artifact you hand to engineering and design.

**Future-state journey: Emotional Music Discovery (Vibe-Checker Pipeline):**

| # | Step | User Does | System Does | Time | Exit Risk |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | **Emotional Prompt Input** | Types: *"Feeling low, need something that lifts me slowly"* into the Vibe Checker input on Home page | **Input Processor** validates prompt, checks cache, sanitizes input | < 0.5 sec | Low — input validation |
| 2 | **Emotion Extraction** | Nothing (waits; sees loading animation) | **Emotion Extraction Engine (LLM)** parses prompt → extracts `current_state: {emotion: "low", energy: "low", valence: 0.3}`, `desired_state: {emotion: "uplifted", energy: "medium", valence: 0.7}`, `transition: "gradual"` | 1–2 sec | Medium — LLM inference variability |
| 3 | **Semantic Retrieval** | Nothing | **Semantic Retrieval Engine** converts extracted emotional profile to embedding query → searches Qdrant for tracks with similar emotional vectors → returns top 50–100 candidate tracks | 0.5–1 sec | Low — deterministic vector search |
| 4 | **Emotion-Aware Ranking** | Nothing | **Ranking Engine** re-ranks candidates using: audio feature alignment (valence, energy, tempo), emotional arc ordering (start low → build gradually), diversity scoring (avoid same artist/genre clusters) | 0.5–1 sec | Low — deterministic ranking |
| 5 | **Vibe Queue Assembly** | Nothing | **Queue Assembler** selects top 10–15 tracks, orders for emotional arc, packages with metadata (track name, artist, album, audio features) | < 0.5 sec | Low |
| 6 | **Queue Display** | Sees Vibe Queue on screen: track list with emotional summary, extracted mood profile displayed | **UI** renders Vibe Queue with emotional context: *"Your Vibe: Low → Uplifted (gradual lift). We found 12 tracks that match."* | Instant (rendering) | Low |
| 7 | **User Review** | Reviews queue; either accepts and begins listening, or enters a new prompt for a different vibe | System ready for next prompt; no follow-up conversation | 0–30 sec (user decision) | Low |
| 8 | **Exception: Low Confidence** | Sees warning: *"We interpreted your vibe as [X]. Refine your prompt for better results."* | System generates shorter queue (5–10 tracks) with confidence warning | Same as happy path | Controlled |
| 9 | **Exception: No Results** | Sees error with example prompts: *"Try: 'peaceful after a long day'"* | System shows helpful error with suggested prompts | < 1 sec | Controlled |

> [!NOTE]
> **Total Time:** < 5 seconds from prompt to full Vibe Queue (vs. 10–20+ minutes manual). The emotional profile is shown to the user for transparency and trust. No skipping, no browsing, no keyword translation needed.

---

### 💬 PM Alignment: Key Design Questions for Step 2

To finalise Step 2, please provide feedback on these key design decisions:

1. **Web Interface Priority:** **Desktop-first with responsive mobile design**
2. **Emotional Profile Display:** Show the extracted emotional profile (current state → desired state) alongside the Vibe Queue so users understand the AI's interpretation
3. **Example Prompts:** Display 4–6 example prompts on the Home page as inspiration for first-time users
4. **Error Recovery:** On failure, always show suggested example prompts and the reason for failure

> **Step 2 Status:** ⏳ **AWAITING PM FEEDBACK**

---

## 📌 Step 3: The System's Job Description

Now that we understand the problem and the user journey, we define what each component of the AI pipeline actually does. This is not technical implementation — it's a clear, human-readable job description for each system component. Engineers will use these to build prompts, schemas, and data flows.

---

### 3.1 System Architecture Overview

The system uses a **Sequential Pipeline with Parallel Retrieval**:

```
User Prompt
     ↓
Input Processor (validation, cache check, sanitization)
     ↓
Emotion Extraction Engine (LLM — Groq Llama-3.1-8B-Instant)
     ↓
Semantic Retrieval Engine (Embedding → Qdrant Vector Search)
     ↓
Emotion-Aware Ranking Engine (Audio feature alignment + emotional arc ordering)
     ↓
Queue Assembler (Top-N selection + arc ordering + metadata packaging)
     ↓
Vibe Queue (displayed to user)
```

---

### 3.2 Input Processor

**Role:** The front gate that validates, sanitizes, and caches user prompts before they enter the AI pipeline.

**Responsibilities:**
- Validate prompt is non-empty and within character limits (max 500 chars)
- Sanitize input (strip HTML, prevent injection, filter harmful content)
- Check Redis cache for identical or near-identical prompts
- If cache hit → return cached Vibe Queue instantly (skip pipeline)
- If cache miss → pass sanitized prompt to Emotion Extraction Engine
- Log prompt (anonymized) for observability

**Inputs:**
- Raw user prompt text
- User session ID (from Google OAuth)

**Outputs:**
- Sanitized prompt (passed to LLM) OR cached Vibe Queue (returned to UI)
- Cache status (hit/miss)

**Key Behaviors:**
- Reject empty prompts with helpful error message and example prompts
- Reject prompts exceeding 500 characters with a polite trim suggestion
- Flag adversarial or harmful prompts (profanity filter, content moderation)
- Cache key = normalized lowercase prompt hash
- Cache TTL = 24 hours

---

### 3.3 Emotion Extraction Engine (LLM)

**Role:** The intelligence core that interprets natural-language emotional expressions and extracts structured emotional signals.

**Responsibilities:**
- Parse free-form emotional language (metaphorical, ambiguous, compound emotions)
- Extract **current emotional state** (primary emotion, secondary emotion, energy level, valence)
- Extract **desired emotional state** (target emotion, target energy, target valence)
- Determine **transition type** (maintain current state, gradual shift, or immediate jump)
- Map extracted emotions to **Spotify audio feature targets** (valence, energy, danceability, tempo, acousticness, instrumentalness, loudness)
- Assign confidence score (0.0–1.0) to the extraction
- Return structured JSON response

**Inputs:**
- Sanitized user prompt (from Input Processor)

**Outputs:**
- Structured emotion profile JSON:

```json
{
  "emotion_type": "mixed_emotion",
  "current_state": {
    "primary_emotion": "lonely",
    "secondary_emotion": "optimistic",
    "energy": "low_medium",
    "valence": 0.45,
    "danceability": 0.3,
    "tempo_range": [70, 100],
    "acousticness": 0.6,
    "instrumentalness": 0.3
  },
  "desired_state": {
    "primary_emotion": "hopeful",
    "secondary_emotion": null,
    "energy": "medium",
    "valence": 0.65,
    "danceability": 0.45,
    "tempo_range": [90, 120],
    "acousticness": 0.4,
    "instrumentalness": 0.2
  },
  "transition": {
    "type": "gradual"
  },
  "confidence": 0.85
}
```

**Emotion Type Classification:**

| Mood Prompt | Emotion Type | `emotion_type` Value |
|---|---|---|
| *"Feeling lonely but optimistic"* | Mixed emotion | `mixed_emotion` |
| *"Feeling low, need something that lifts me slowly"* | Current + desired outcome | `current_with_desired` |
| *"Give me something nostalgic"* | Desired emotion only | `desired_only` |
| *"I feel emotionally exhausted"* | Current emotion only | `current_only` |

**Model:** Groq — Llama-3.1-8B-Instant (fast inference, low cost, sufficient for structured emotion extraction)

**Key Behaviors:**
- Classify `emotion_type` for every prompt: `mixed_emotion`, `current_with_desired`, `desired_only`, or `current_only`
- Extract `primary_emotion` and `secondary_emotion` in both `current_state` and `desired_state` (secondary can be `null`)
- Handle metaphorical language: *"music that feels like rain"* → extract cathartic calm, not literal rain sounds
- Handle compound emotions: *"angry but want to calm down"* → `current_with_desired`, anger (current) → calm (desired) with gradual transition
- Handle mixed emotions: *"feeling lonely but optimistic"* → `mixed_emotion`, primary=lonely, secondary=optimistic
- Handle vague input: *"something chill"* → `desired_only`, infer neutral current state, default low energy + high acousticness
- Handle contradictions gracefully: *"happy sad"* → `mixed_emotion`, extract bittersweet with confidence penalty
- When `emotion_type` is `desired_only`, infer a neutral current state automatically
- When `emotion_type` is `current_only`, set desired state = current state with `maintain` transition
- Always return a valid JSON response, even for edge cases
- Map to **all available Spotify audio features**, not just valence and energy

**Prompt Engineering Principles:**

| Principle | Meaning |
|-----------|---------|
| **Emotion type classification** | Always classify the prompt's emotion pattern before extraction |
| **Dual-emotion awareness** | Extract both primary and secondary emotions in each state when present |
| **Dual-state awareness** | Always extract both current and desired states, even if user only describes one |
| **Conservative confidence** | Assign lower confidence for ambiguous, contradictory, or vague prompts |
| **Feature completeness** | Map to all Spotify audio features (valence, energy, danceability, tempo, acousticness, instrumentalness, loudness) |
| **Grounded output** | All audio feature values must be within valid Spotify ranges (0.0–1.0 for most, BPM for tempo) |

---

### 3.4 Semantic Retrieval Engine

**Role:** The search layer that finds candidate tracks whose emotional embeddings are closest to the user's extracted emotional profile.

**Responsibilities:**
- Convert the extracted emotional profile into an embedding query vector using BAAI/bge-small-en-v1.5
- Execute similarity search against pre-indexed Qdrant vector database
- Apply metadata filters (optional: genre preference, release year range, popularity threshold)
- Return top 50–100 candidate tracks with similarity scores
- Handle sparse results gracefully (< 20 candidates triggers soft failure warning)

**Inputs:**
- Structured emotion profile (from Emotion Extraction Engine)
- Optional metadata filters (if implemented)

**Outputs:**
- List of candidate tracks with:
  - Track ID, name, artist, album
  - Similarity score
  - Audio features (valence, energy, danceability, tempo, acousticness, instrumentalness, loudness, speechiness, liveness, mode)

**Technology:**
- Embedding model: BAAI/bge-small-en-v1.5
- Vector database: Qdrant Cloud (Free Tier)
- Similarity metric: Cosine similarity
- Dataset: [Spotify Tracks Dataset (HuggingFace)](https://huggingface.co/datasets/maharshipandya/spotify-tracks-dataset)

**Key Behaviors:**
- Pre-index all tracks at ingestion time (one-time batch process)
- Search by emotional embedding similarity, not keyword matching
- Return enough candidates (50–100) for ranking engine to work with diversity
- Apply metadata filters as post-retrieval refinement, not primary search constraint
- Handle Qdrant timeouts with retry logic (max 3 retries)
- Log search latency and result count for observability

---

### 3.5 Emotion-Aware Ranking Engine

**Role:** The quality layer that re-ranks candidate tracks based on emotional alignment, audio feature matching, and queue coherence.

**Responsibilities:**
- Re-rank candidate tracks from Semantic Retrieval Engine using multi-factor scoring
- Score each track on **emotional alignment** (how well its audio features match the emotional profile)
- Score each track on **arc positioning** (where it belongs in the Current → Target transition)
- Score each track on **diversity** (penalize same-artist clusters, same-genre saturation)
- Apply transition-aware ordering: for "gradual" transitions, order tracks along the emotional gradient (start at current state, end at desired state)
- For "maintain" transitions, keep consistent emotional level throughout
- For "immediate" transitions, jump to desired state after 1–2 transitional tracks

**Inputs:**
- Candidate tracks with similarity scores (from Semantic Retrieval Engine)
- Structured emotion profile with transition type (from Emotion Extraction Engine)

**Outputs:**
- Re-ranked track list with composite scores
- Track position assignments (early/mid/late in queue based on emotional arc)

**Scoring Formula:**

```
composite_score = (
    w1 × emotional_alignment_score +
    w2 × arc_position_score +
    w3 × diversity_score +
    w4 × vector_similarity_score
)
```

Where:
- `w1 = 0.35` (emotional alignment — primary signal)
- `w2 = 0.25` (arc position — emotional journey coherence)
- `w3 = 0.15` (diversity — avoid monotony)
- `w4 = 0.25` (vector similarity — semantic relevance)

**Key Behaviors:**
- Emotional alignment compares track's `valence`, `energy`, `danceability`, `tempo`, `acousticness` against the emotional profile's target values
- Arc positioning assigns each track to early (current state), mid (transition), or late (desired state) based on its audio features relative to the full emotional gradient
- Diversity scoring penalizes consecutive tracks from the same artist or with very similar audio feature profiles
- Weights are configurable and can be tuned based on user feedback data in future versions
- Handle edge cases: if only 5–10 candidates, skip diversity penalty to avoid empty queue

---

### 3.6 Queue Assembler

**Role:** The final assembly layer that selects the top tracks and packages them into a user-facing Vibe Queue.

**Responsibilities:**
- Select top 10–15 tracks from ranked list
- Enforce emotional arc order (not just score order — position matters)
- Package each track with display metadata (name, artist, album, key audio features)
- Generate emotional summary text: *"Your Vibe: Lonely → Hopeful (gradual lift). 12 tracks matched."*
- Store assembled queue in Redis cache (keyed to normalized prompt hash)
- Return final Vibe Queue to UI

**Inputs:**
- Ranked and position-assigned tracks (from Ranking Engine)
- Emotional profile summary (from Emotion Extraction Engine)

**Outputs:**
- Vibe Queue object:

```json
{
  "prompt": "feeling low, need something that lifts me slowly",
  "emotion_type": "current_with_desired",
  "emotional_profile": {
    "current": {
      "primary_emotion": "low",
      "secondary_emotion": null
    },
    "desired": {
      "primary_emotion": "uplifted",
      "secondary_emotion": "hopeful"
    },
    "transition": "gradual"
  },
  "tracks": [
    {
      "position": 1,
      "track_name": "Skinny Love",
      "artist": "Bon Iver",
      "album": "For Emma, Forever Ago",
      "valence": 0.28,
      "energy": 0.25
    },
    {
      "position": 2,
      "track_name": "...",
      "artist": "..."
    }
  ],
  "queue_size": 12,
  "confidence": 0.85,
  "generated_at": "2026-06-28T18:30:00Z"
}
```

**Key Behaviors:**
- Always return at least 5 tracks (soft failure path), ideally 10–15
- Emotional summary must be human-readable, not raw JSON
- Cache the queue for 24 hours to serve identical prompts instantly
- Include confidence score in response so UI can show warnings if low
- Include arc labels ("current_state", "transition", "desired_state") for UI display

---

### 3.7 Authentication & Session Layer

**Role:** Manages user identity and session state via Google OAuth through Supabase.

**Responsibilities:**
- Google OAuth sign-in / sign-up flow
- JWT session token management
- Associate prompts and queues with authenticated user sessions
- Rate limiting per user (max 20 prompts/hour)

**Technology:**
- Supabase Auth (Google OAuth provider)
- JWT tokens for session management
- PostgreSQL (Supabase) for user metadata

**Key Behaviors:**
- OAuth flow should be frictionless — sign in with Google in 2 clicks
- Session tokens expire after 24 hours; auto-refresh on active sessions
- Anonymous users can try 3 prompts before being prompted to sign in (growth strategy)
- Rate limiting is per-user, not per-IP, to prevent abuse while allowing power users

---

### 3.8 Caching Layer

**Role:** Reduces latency and LLM API costs by serving cached Vibe Queues for repeated or identical prompts.

**Responsibilities:**
- Store generated Vibe Queues keyed to normalized prompt hash
- Serve cached results for identical prompts (< 50ms response)
- Track cache hit/miss rates for observability
- Invalidate cache after TTL expiry (24 hours)

**Technology:**
- Redis (in-memory key-value store)

**Key Behaviors:**
- Normalize prompt before hashing: lowercase, strip extra whitespace, remove punctuation
- Cache only successful queue generations (not errors or soft failures)
- Track cache hit rate as a key operational metric
- Consider semantic similarity caching in v2 (serve cached queue for prompts with > 95% semantic similarity)

---

### 3.9 Data Ingestion Pipeline (One-Time Setup)

**Role:** Pre-processes and indexes the Spotify Tracks Dataset for vector search.

**Responsibilities:**
- Download and parse the [Spotify Tracks Dataset](https://huggingface.co/datasets/maharshipandya/spotify-tracks-dataset)
- Extract audio features (valence, energy, danceability, tempo, acousticness, instrumentalness, loudness, speechiness, liveness, mode)
- Generate text descriptions for each track based on audio features (e.g., "a low-energy, high-valence acoustic track with slow tempo")
- Embed text descriptions using BAAI/bge-small-en-v1.5
- Index embeddings + metadata into Qdrant Cloud
- Store raw metadata in Supabase (PostgreSQL) for display and filtering

**Inputs:**
- Raw Spotify Tracks Dataset (CSV/Parquet from HuggingFace)

**Outputs:**
- Qdrant collection with track embeddings and metadata
- Supabase table with full track metadata

**Key Behaviors:**
- One-time batch process (run once at project setup; re-run on dataset updates)
- Generate meaningful text descriptions — not just concatenated feature values
- Handle missing data gracefully (skip tracks with null audio features)
- Log ingestion statistics: total tracks processed, success rate, embedding dimensions

---

### 3.10 Component Communication Protocols

**Data Flow:**
- All components communicate via structured JSON payloads
- Each component receives typed input and produces typed output
- REST API endpoints expose the pipeline to the frontend
- Redis mediates caching between Input Processor and Queue Assembler

**API Contract:**

| Endpoint | Method | Input | Output | Latency Target |
| :--- | :--- | :--- | :--- | :--- |
| `/api/vibe` | POST | `{ "prompt": "feeling low..." }` | Vibe Queue JSON | < 5 sec |
| `/api/auth/google` | POST | Google OAuth token | JWT session token | < 1 sec |
| `/api/examples` | GET | None | List of example prompts | < 100ms |
| `/api/health` | GET | None | System health status | < 100ms |

**Error Propagation:**
- Each component reports errors with specific context and error codes
- Errors propagate up the pipeline: extraction failure → no retrieval → no queue
- All errors are logged with request IDs for debugging
- User-facing errors are always human-readable with suggested actions

---

### 3.11 Component Performance Expectations

**Latency Targets:**

| Component | Latency Target | Notes |
| :--- | :--- | :--- |
| Input Processor | < 100ms | Validation + cache check |
| Emotion Extraction (LLM) | 1–2 sec | Groq inference (fast) |
| Semantic Retrieval (Qdrant) | 0.5–1 sec | Vector search over indexed dataset |
| Ranking Engine | 0.5–1 sec | Deterministic scoring and sorting |
| Queue Assembler | < 200ms | Selection and packaging |
| **Total Pipeline** | **< 5 sec** | **End-to-end from prompt to queue** |
| Cache Hit | < 50ms | Bypass entire pipeline |

**Quality Targets:**

| Metric | Target | Measurement |
| :--- | :--- | :--- |
| Emotion extraction accuracy | ≥ 80% | User rates extracted profile as matching their intent |
| Emotional alignment of queue | ≥ 75% | User rates queue as emotionally relevant |
| Pipeline success rate | ≥ 95% | % of prompts that produce a valid Vibe Queue |
| Cache hit rate | ≥ 20% (after 30 days) | % of prompts served from cache |

**Failure Handling:**

| Failure Type | Handling Strategy |
| :--- | :--- |
| LLM timeout | Retry once with shorter prompt; if still fails → hard failure with error message |
| LLM invalid JSON | Retry once with stricter prompt; if still fails → hard failure |
| Qdrant timeout | Retry up to 3 times with exponential backoff; if still fails → hard failure |
| < 5 results from search | Soft failure → generate shorter queue with warning |
| Redis down | Bypass cache; process all prompts through full pipeline (degraded performance, not failure) |

---

### 3.12 Prompt Engineering Specification

#### LLM System Prompt Design

The Emotion Extraction Engine's system prompt must enforce:

| Requirement | Implementation |
|-------------|----------------|
| **Structured output** | Always return valid JSON matching the emotion profile schema |
| **Dual-state extraction** | Extract both current_state and desired_state, even when user only mentions one |
| **Conservative confidence** | Confidence < 0.5 for vague prompts; > 0.8 only for clear, specific emotional language |
| **Audio feature mapping** | Map emotions to Spotify audio features using domain knowledge of music-emotion relationships |
| **Graceful handling** | For nonsensical input, return low confidence with best-effort extraction rather than error |
| **No hallucination** | Audio feature values must be within valid Spotify ranges; do not invent emotions not present in prompt |

#### Tone & Interaction Style

- The system does not converse — it processes and responds
- Emotional summaries should be warm but concise: *"Your Vibe: Lonely → Hopeful"*
- Error messages should be empathetic, not clinical: *"We couldn't quite catch that vibe"* not *"Input parsing error"*
- Example prompts should feel natural and relatable, not robotic

---

### 💬 PM Alignment: Key Design Questions for Step 3

To finalise Step 3, please provide feedback on these key system design decisions:

1. **Queue Size:** **10–15 tracks** per Vibe Queue (default). Is this the right range?
2. **Ranking Weights:** Emotional alignment (0.35), arc position (0.25), similarity (0.25), diversity (0.15). Should any weight be adjusted?
3. **Cache Strategy:** 24-hour TTL for identical prompt caching. Should we also implement semantic similarity caching (serve cached queue for near-identical prompts)?
4. **Anonymous Access:** Allow 3 free prompts before requiring Google sign-in. Is this the right threshold for conversion?

> **Step 3 Status:** ⏳ **AWAITING PM FEEDBACK**

---

## 📊 Summary: Vibe-Checker Product Strategy at a Glance

| Dimension | Decision |
| :--- | :--- |
| **Problem** | Spotify cannot understand real-time emotional intent — users must self-translate emotions to keywords |
| **Solution** | LLM-powered pipeline: emotional prompt → structured extraction → vector search → ranked Vibe Queue |
| **Why AI** | Emotional language is unbounded, metaphorical, and dual-state — no rules-based system can handle it |
| **Primary Flow** | One prompt → One Vibe Queue (single-turn, no conversation) |
| **Target Latency** | < 5 seconds end-to-end |
| **Queue Size** | 10–15 tracks per queue |
| **LLM** | Groq Llama-3.1-8B-Instant (emotion extraction) |
| **Embeddings** | BAAI/bge-small-en-v1.5 (semantic retrieval) |
| **Vector DB** | Qdrant Cloud (free tier) |
| **Metadata DB** | Supabase (PostgreSQL) |
| **Cache** | Redis (24h TTL) |
| **Auth** | Google OAuth via Supabase |
| **Dataset** | Spotify Tracks Dataset (HuggingFace — public) |
| **Touchpoint** | Web app with persistent Vibe Checker input on Home page |
| **v1 Scope** | Text-only, single-turn, no playback, no feedback learning |

---
