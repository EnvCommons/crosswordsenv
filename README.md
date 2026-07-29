# Crosswords

[![OpenReward Environment](https://img.shields.io/badge/%E2%AD%90%20OpenReward-Environment-f7e6cc)](https://openreward.ai/GeneralReasoning/Crosswords)

## Description

**Crosswords** is an environment for evaluating agents on crossword puzzle solving. This environment wraps the Crosswords implementation from [TextArena](https://github.com/LeonGuertler/TextArena), a framework for text-based game environments.

## Capabilities

- Natural language understanding and vocabulary knowledge
- Constraint satisfaction with intersecting words
- Reasoning about clues and word patterns

## Compute Requirements

Crosswords does not require a sandbox. It has minimal compute requirements.

## License

[MIT](https://github.com/LeonGuertler/TextArena/blob/main/LICENSE).

## Tasks

There are two splits: train (300 tasks) and test (300 tasks). Each split contains 50 tasks across each of 6 variants:

- **Crosswords-v0**: Standard crossword puzzle
- **Crosswords-v0-train**: Training variant with guidance
- **Crosswords-v0-raw**: Raw feedback without formatting
- **Crosswords-v0-hardcore**: More challenging puzzles
- **Crosswords-v0-hardcore-train**: Hardcore with training guidance
- **Crosswords-v0-hardcore-raw**: Hardcore with raw feedback

Each task is seeded for reproducibility.

## Reward Structure

This is a sparse reward environment. TextArena's Crosswords reward is already in `[0.0, 1.0]` and is passed through unchanged: completing the puzzle scores `1.0`, and every other terminal outcome (turn limit or an invalid placement) scores the fraction of letter cells correctly filled. Intermediate placements score `0.0`.

We do not use LLM graders for this environment; reward is determined programmatically.

## Data

Game state is generated procedurally by the TextArena engine using seeded randomness. No external data files are required.

## Tools

Agents are given a single tool:

- `place_letter(row, column, letter)`: Place a letter on the crossword grid at the given row and column (0-indexed).

## Time Horizon

Crosswords is a multi-turn environment.

## Environment Difficulty

Medium to Hard. The difficulty varies across variants, with hardcore versions requiring deeper vocabulary knowledge and more complex reasoning about word intersections.

## Other Environment Requirements

There are no further environment requirements; Crosswords works out of the box without any secrets or API keys.

## Safety

Agents in Crosswords interact only with a word puzzle game and have no access to external systems, the internet, or sensitive data. The environment does not present safety risks.

## Citations

```bibtex
@software{textarena2024,
  author    = {Guertler, Leon and Banting, Wilfried and Pignatelli, Eduardo},
  title     = {TextArena},
  year      = {2024},
  publisher = {GitHub},
  url       = {https://github.com/LeonGuertler/TextArena}
}
```
