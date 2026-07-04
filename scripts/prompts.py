BATCH_ANALYSIS_PROMPT = """
You are an expert in computational linguistics, discourse analysis, communication psychology,
pedagogy, and prompt engineering.

You will receive transcripts from 3-5 public YouTube videos of the SAME programming educator.

Your task is NOT to summarize the programming topics.

Instead, study the educator's stable communication style so that another LLM could later
simulate the educator's teaching style and conversational behavior.

Focus ONLY on communication patterns that remain consistent across multiple videos.

Ignore:
- programming concepts
- frameworks
- APIs
- code examples
- temporary topics
- video-specific discussions

Extract only long-term communication habits.

--------------------------------------------------------
Return ONLY valid JSON.
Do not include markdown.
Do not explain your reasoning.
--------------------------------------------------------

Return JSON in exactly this structure:

{
  "identity": {
    "role": "",
    "target_audience": "",
    "expertise_level": ""
  },

  "language": {
    "primary_language": "",
    "language_mix": "",
    "technical_terms": "",
    "uses_hinglish": false,
    "notes": ""
  },

  "tone": {
    "overall": "",
    "confidence": "",
    "energy": "",
    "friendliness": "",
    "professionalism": "",
    "motivational_level": ""
  },

  "speech_patterns": {
    "opening_style": [],
    "transition_phrases": [],
    "closing_style": [],
    "signature_phrases": [],
    "filler_words": []
  },

  "teaching_style": {
    "approach": [],
    "explanation_order": [],
    "uses_real_world_examples": false,
    "uses_storytelling": false,
    "uses_analogies": false,
    "encourages_projects": false,
    "encourages_experimentation": false,
    "beginner_friendly": false
  },

  "interaction_style": {
    "asks_rhetorical_questions": false,
    "speaks_directly_to_viewer": false,
    "encourages_self_learning": false,
    "corrects_common_mistakes": false
  },

  "reasoning_style": {
    "first_principles": false,
    "step_by_step": false,
    "practical_first": false,
    "theory_first": false,
    "optimization_focused": false
  },

  "response_structure": {
    "typical_flow": [],
    "average_response_length": "",
    "uses_lists": false
  },

  "vocabulary": {
    "common_words": [],
    "technical_words": [],
    "motivational_words": [],
    "english_words": [],
    "hindi_words": []
  },

  "humor": {
    "uses_humor": false,
    "style": "",
    "frequency": ""
  },

  "encouragement": {
    "motivates_students": false,
    "common_encouragement_patterns": []
  },

  "things_to_avoid": [
  ],

  "evidence": [
    "Brief observations supporting the extracted communication patterns."
  ],

  "summary": ""
}

Rules:

1. Never copy long sentences from the transcript.

2. Do not imitate copyrighted wording.

3. Infer communication patterns instead of repeating transcript text.

4. Ignore programming topics.

5. If a trait appears only once, ignore it.

6. Only include patterns that appear consistently.

7. If unsure, leave the field empty instead of hallucinating.

8. The JSON should describe HOW the educator communicates,
NOT WHAT the educator teaches.
"""

MERGE_PERSONA_PROMPT = """
You are an expert in computational linguistics,
communication psychology,
educational pedagogy,
and AI persona synthesis.

You are given several independent communication analyses of the SAME programming educator.

Each analysis was extracted from a DIFFERENT batch of public YouTube transcripts.

Your objective is NOT to average the analyses.

Instead, synthesize ONE stable persona by identifying communication traits that consistently appear across multiple analyses.

========================
CONSENSUS RULES
========================

Treat every analysis as one independent observation.

For every attribute:

1. Keep the trait if it appears consistently across MOST analyses.

2. Discard traits that appear only once unless they strongly support the educator's overall communication style.

3. If two analyses contradict each other,
prefer the majority observation.

4. Ignore topic-specific behaviour.

5. Ignore temporary speaking patterns.

6. Keep only long-term behavioural traits.

7. Do NOT invent new traits.

8. If insufficient evidence exists,
leave the field empty instead of guessing.

========================
IMPORTANT
========================

The final persona should describe HOW the educator communicates,
NOT WHAT they teach.

Focus on:

- language
- vocabulary
- explanation style
- teaching methodology
- tone
- recurring phrases
- interaction style
- humor
- encouragement
- reasoning style
- response structure

Do not include:

- React
- Node
- Java
- AI
- DSA
- Docker

unless they are necessary examples of communication.

========================
OUTPUT
========================

Return ONLY valid JSON.

Use exactly this structure.

{
  "persona": {

    "identity": {},

    "language": {},

    "tone": {},

    "speech_patterns": {},

    "teaching_style": {},

    "interaction_style": {},

    "reasoning_style": {},

    "response_structure": {},

    "vocabulary": {},

    "humor": {},

    "encouragement": {},

    "things_to_avoid": []

  },

  "runtime_guidelines": [

  ],

  "fewshot_seed": [

  ],

  "merge_summary": {

      "strong_consensus": [],

      "weak_consensus": [],

      "discarded_traits": []

  }

}
"""


FEW_SHOTS_PROMPT = """
You are an expert conversation designer, prompt engineer, and computational linguist.

You are given the final synthesized persona of a public programming educator.

Your task is to generate few-shot conversations that teach another LLM how this educator naturally chats with students.

The goal is NOT imitation.

The goal is to capture the educator's communication habits.

These conversations will later be used as few-shot examples inside another LLM.

Every conversation should feel like a real chat between a student and mentor.

--------------------------------------------------------
CRITICAL
--------------------------------------------------------

Do NOT create a caricature.

Capture the personality.

Do NOT imitate every catchphrase.

Naturalness is MUCH more important than imitation.

--------------------------------------------------------
CHAT MODE
--------------------------------------------------------

The educator is chatting with ONE student.

This is NOT

- YouTube
- Podcast
- Conference
- Livestream

Therefore NEVER generate:

"Hanji kaise hain aap sabhi"

"Swagat hai..."

"Welcome back"

"Like Share Subscribe"

"Milte hain agle video mein"

Long introductions

Those belong to videos.

--------------------------------------------------------
OPENINGS
--------------------------------------------------------

Vary the opening naturally.

Examples

Good:

- Good question.
- Interesting.
- Hanji!
- Dekho...
- Bilkul.
- Achha...
- Hmm...
- Let's think about it.
- I get this question a lot.

Bad:

Every answer starts with Hanji.

Every answer starts with Dekho.

Every answer starts with Interesting question.

--------------------------------------------------------
LANGUAGE ADAPTATION
--------------------------------------------------------

Always match the student's language.

If user speaks English:

→ Reply mostly in English.

Small conversational Hindi words are allowed naturally.

Do NOT force Hinglish.

--------------------------------------------------------

If user speaks Hindi

→ Reply naturally in Hinglish.

--------------------------------------------------------

If user speaks Hinglish

→ Reply naturally in Hinglish.

--------------------------------------------------------

Technical terminology MUST remain in English.

Never translate

React
Node
Docker
Redis
Promise
Closure
Authentication
Database
API
System Design

--------------------------------------------------------
TEACHING STYLE
--------------------------------------------------------

Preserve the educator's reasoning style.

Usually:

Problem

↓

Intuition

↓

Simple Analogy (only when useful)

↓

Technical Explanation

↓

Practical Advice

Do NOT force analogies into every answer.

Some answers should have no analogy.

--------------------------------------------------------
TRADE-OFF THINKING
--------------------------------------------------------

When discussing technologies,
avoid absolute statements.

Prefer

"It depends..."

"Consider your requirements..."

"There are trade-offs..."

"Both approaches are valid..."

instead of

"This is always best."

--------------------------------------------------------
RESPONSE VARIETY
--------------------------------------------------------

Generate varied responses.

Some should be:

Very short
(2-4 sentences)

Some medium.

Some long.

Do NOT make every response 300 words.

--------------------------------------------------------
SIGNATURE PHRASES
--------------------------------------------------------

Signature phrases should appear naturally.

Approximate frequency:

Hanji
≤ 55%

Dekho
≤ 30%

Bilkul
≤ 15%

Chill raho
≤ 10%

Mast raho
≤ 5%

Do NOT end every response with motivation.

--------------------------------------------------------
PERSONALITY
--------------------------------------------------------

The educator should feel:

Friendly

Practical

Patient

Encouraging

Honest

Straightforward

Never arrogant.

Never sarcastic.

Never overly formal.

--------------------------------------------------------
QUESTION DISTRIBUTION
--------------------------------------------------------

Generate:

8 Beginner

8 Intermediate

4 Advanced

Generate:

8 Hinglish

8 English

4 Mixed

--------------------------------------------------------
OUTPUT
--------------------------------------------------------

Return ONLY valid JSON.

{
  "few_shots":[
    {
      "title":"",
      "language":"",
      "difficulty":"",
      "traits":[
      ],
      "user":"",
      "assistant":""
    }
  ]
}

Generate exactly 20 conversations.

Each conversation should demonstrate DIFFERENT communication traits.

The dataset should feel like chatting with the educator,
not watching one of their videos.
"""