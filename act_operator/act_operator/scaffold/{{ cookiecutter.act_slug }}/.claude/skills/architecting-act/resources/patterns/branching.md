# Branching Pattern

Routes to different paths based on conditions.

## Structure

```
START → Classifier → {
    condition_a → HandlerA → END
    condition_b → HandlerB → END
    default → Fallback → END
}
```

## When to Use

- Different inputs need different processing
- Multiple specialized handlers exist
- Classification/routing logic required

## Design Checklist

- [ ] Decision criteria clearly defined
- [ ] All possible branches covered
- [ ] Default/fallback path exists
- [ ] Conditions are mutually exclusive

## Common Mistakes

**Non-exhaustive conditions:** Always add default/fallback.

**Overlapping conditions:** Make mutually exclusive.

**Too many branches:** More than 5 = consider redesign.

## Example: Intent Router

```
START → ClassifyIntent → {
    "question" → QuestionHandler
    "command" → CommandHandler
    "chitchat" → ChitchatHandler
    default → FallbackHandler
} → END
```
