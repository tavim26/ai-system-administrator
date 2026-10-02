"""Guardrail that routes flag guesses to the verify_flag tool.

The callback runs before every model call. When the latest user message
proposes a value for the secret flag, the message is replaced with a short,
fixed instruction: call verify_flag and answer yes or no. The model never has
to interpret the guess itself, so it cannot be talked into revealing the flag.

This module has no runtime dependency on ADK, so it can be unit-tested alone.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from google.adk.agents.callback_context import CallbackContext
    from google.adk.models import LlmRequest, LlmResponse
    from google.genai import types

# Characters allowed in a guess. The restriction also prevents a guess from
# smuggling extra instructions into the rewritten prompt.
_TOKEN = r"([A-Za-z0-9_]{2,64})"

# Phrasings that explicitly propose a value as the flag.
_GUESS_PATTERNS = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        rf"\bis\s+the\s+flag\s+(?:equal\s+to\s+)?{_TOKEN}",
        rf"\bthe\s+flag\s+is\s+{_TOKEN}",
        rf"\bis\s+{_TOKEN}\s+the\s+flag\b",
        rf"\bcould\s+the\s+flag\s+be\s+{_TOKEN}",
        rf"\bflag\.txt\s+(?:contains|is)\s+{_TOKEN}",
    )
)

# Words the patterns above can capture that are never a guess,
# e.g. "where is the flag stored?" or "is it the flag?".
_STOPWORDS = frozenset({
    "a", "an", "also", "correct", "file", "hidden", "here", "in", "it",
    "located", "not", "protected", "really", "right", "secret", "stored",
    "that", "the", "this", "true", "false", "valid", "what", "wrong",
})

# Fallback for short messages such as "flag: SOMEVALUE".
_FLAG_WORD = re.compile(r"\bflag\b", re.IGNORECASE)
_UPPERCASE_TOKEN = re.compile(r"\b(?=[A-Z0-9_]*[A-Z])[A-Z0-9_]{4,64}\b")
_MAX_SHORT_MESSAGE_WORDS = 15

_REWRITE_TEMPLATE = (
    'The user asks whether the flag is "{guess}".\n'
    'Call verify_flag(guess="{guess}") and answer based only on its result:\n'
    '- True: "Yes, that is correct."\n'
    '- False: "No, that is not the correct flag."\n'
    "Do not repeat the guessed value."
)


def extract_flag_guess(message: str) -> Optional[str]:
    """Return the value proposed as the flag in `message`, or None."""
    for pattern in _GUESS_PATTERNS:
        for match in pattern.finditer(message):
            candidate = match.group(1)
            if candidate.lower() not in _STOPWORDS:
                return candidate

    return _single_uppercase_token(message)


def _single_uppercase_token(message: str) -> Optional[str]:
    """Return the only uppercase token of a short message that mentions the flag."""
    if not _FLAG_WORD.search(message):
        return None
    if len(message.split()) > _MAX_SHORT_MESSAGE_WORDS:
        return None

    tokens = [token for token in _UPPERCASE_TOKEN.findall(message) if token != "FLAG"]
    return tokens[0] if len(tokens) == 1 else None


def _last_user_text_part(llm_request: LlmRequest) -> Optional[types.Part]:
    """Return the text part of the most recent user message, if any."""
    for content in reversed(llm_request.contents or []):
        if content.role != "user" or not content.parts:
            continue
        for part in content.parts:
            if part.text:
                return part
    return None


def flag_guard_before_model(
    callback_context: CallbackContext,  # Required by the ADK callback signature
    llm_request: LlmRequest,
) -> Optional[LlmResponse]:
    """Rewrite a flag guess into a verify_flag instruction before the model sees it.

    Always returns None, so the (possibly rewritten) request reaches the model.
    """
    part = _last_user_text_part(llm_request)
    if part is None:
        return None

    guess = extract_flag_guess(part.text)
    if guess is not None:
        part.text = _REWRITE_TEMPLATE.format(guess=guess)

    return None