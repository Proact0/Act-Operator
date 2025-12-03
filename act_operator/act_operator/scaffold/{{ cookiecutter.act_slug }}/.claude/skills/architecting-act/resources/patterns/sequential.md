# Sequential Pattern

Linear chain where each step depends on the previous.

## Structure

```
START → Step1 → Step2 → Step3 → ... → END
```

## When to Use

- Each step depends on previous output
- Order cannot change
- No decision points needed

## Design Checklist

- [ ] Input clearly defined
- [ ] Each step has single responsibility
- [ ] Output matches requirements
- [ ] 3-7 nodes typical

## Common Mistakes

**Too many nodes:** Combine trivial steps.

**Too few nodes:** Split if node does multiple things.

**Missing validation:** Fail fast on bad input.

## Example: Document Processing

```
START → ParseDocument → CleanContent → ExtractEntities → GenerateSummary → END
```
