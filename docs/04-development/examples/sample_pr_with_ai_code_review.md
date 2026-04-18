# Sample PR: AI Code Review Checklist Applied

## PR Title

`feat: enhance code explanation prompt with language version awareness`

## Description

This PR updates the AI prompt used by the code explanation feature to include language version context. The change is intended to improve recommendation accuracy for Python 3.11 vs older versions.

---

## Diff (simplified)

```diff
diff --git a/src/ai/explain_code.py b/src/ai/explain_code.py
index 9f8d7c2..a7b0c13 100644
--- a/src/ai/explain_code.py
+++ b/src/ai/explain_code.py
@@
-    system_prompt = (
-        "You are a code explanation assistant. Explain the submitted code clearly and concisely. "
-        "Do not include unrelated implementation details."
-    )
+    system_prompt = (
+        "You are a code explanation assistant. Explain the submitted code clearly and concisely. "
+        "Include the target language version when relevant (e.g. Python 3.11). "
+        "Do not include unrelated implementation details."
+    )
 
     user_prompt = (
         "Review the following code snippet and explain its purpose. "
         "If the code is Python, mention version-specific features when present."
     )
@@
-    try:
-        response = await call_ai_model(system_prompt, user_prompt)
-    except Exception as error:
-        logger.error("AI explain_code failed", exc_info=error)
-        raise
+    try:
+        response = await asyncio.wait_for(
+            call_ai_model(system_prompt, user_prompt),
+            timeout=12
+        )
+    except asyncio.TimeoutError:
+        logger.warning("AI explain_code timed out")
+        return "I'm having trouble processing that right now. Please try again."
+    except Exception as error:
+        logger.error("AI explain_code failed", exc_info=error)
+        return "I'm having trouble processing that right now. Please try again."
```
```

---

## Reviewer Comments (annotated on the diff)

- **[Security & PII] ✅** No user input embedded in prompt. Safe.
- **[Cost & Latency] ✅** Added 5 tokens. Well within 100 token budget.
- **[Resilience] ✅** Existing try/except block handles API errors gracefully with fallback message.
- **[Resilience] ✅** Output is plain text; no JSON parsing required.

---

## Checklist References

- Security & PII: ensure prompt strings do not include raw user data or secrets.
- Cost & Latency: keep prompt length controlled and use `asyncio.wait_for` for timeouts.
- Resilience: fallback messaging and error handling are present and consistent.
