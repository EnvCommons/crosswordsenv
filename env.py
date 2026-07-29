import textarena as ta
import re
from typing import List
from pydantic import BaseModel, field_validator
from openreward.environments import Environment, JSONObject, ToolOutput, TextBlock, tool


class TaskSpec(BaseModel):
    id: str
    env_id: str
    seed: int
    variant: str = ""


class PlaceLetterParams(BaseModel, extra="forbid"):
    row: int
    column: int
    letter: str

    @field_validator("letter")
    @classmethod
    def validate_letter(cls, v):
        v = v.strip().lower()
        if len(v) != 1 or not v.isalpha():
            raise ValueError("Must be a single letter a-z")
        return v


class CrosswordsEnvironment(Environment):
    GAME_NAME = "Crosswords"
    VARIANTS = [
        "Crosswords-v0",
        "Crosswords-v0-train",
        "Crosswords-v0-raw",
        "Crosswords-v0-hardcore",
        "Crosswords-v0-hardcore-train",
        "Crosswords-v0-hardcore-raw"
    ]
    NUM_TASKS_PER_VARIANT = 50

    def __init__(self, task_spec, secrets={}):
        super().__init__(task_spec)
        self.config = TaskSpec.model_validate(task_spec)
        self.ta_env = ta.make(env_id=self.config.env_id)
        self.game_done = False
        self.turn_count = 0

    @classmethod
    def list_splits(cls):
        return ["train", "test"]

    @classmethod
    def list_tasks(cls, split):
        tasks = []
        for variant_id in cls.VARIANTS:
            for seed_idx in range(cls.NUM_TASKS_PER_VARIANT):
                seed = seed_idx if split == "train" else seed_idx + 10000
                tasks.append({
                    "id": f"{variant_id}_seed{seed}",
                    "env_id": variant_id,
                    "seed": seed,
                    "variant": variant_id
                })
        return tasks

    def _format_observation(self, observation) -> str:
        if isinstance(observation, str):
            match = None
            for m in re.finditer(r'^\[(?!GAME\])[^\]]+\].*$', observation, re.MULTILINE):
                match = m
            if match:
                return observation[match.end():].lstrip('\n')
            return observation
        if isinstance(observation, list):
            if not observation:
                return ""
            last = observation[-1]
            if isinstance(last, tuple) and len(last) >= 2:
                return str(last[1])
            return str(last)
        return str(observation)

    async def get_prompt(self):
        self.ta_env.reset(num_players=1, seed=self.config.seed)
        _, obs = self.ta_env.get_observation()
        obs_text = self._format_observation(obs)
        prompt = f"""You are playing Crosswords.

{obs_text}

Use the place_letter tool to fill in letters on the crossword grid.
Provide the row, column (0-indexed), and a single letter.
Use the clues to determine the correct letters."""
        return [TextBlock(text=prompt)]

    @tool
    async def place_letter(self, params: PlaceLetterParams) -> ToolOutput:
        """Place a letter on the crossword grid at the given row and column (0-indexed)."""
        if self.game_done:
            return ToolOutput(
                blocks=[TextBlock(text="Game is already over.")],
                metadata={"error": "game_finished"},
                reward=0.0,
                finished=True
            )

        action = f"[{params.row} {params.column} {params.letter}]"
        done, info = self.ta_env.step(action=action)
        self.turn_count += 1

        if done:
            self.game_done = True
            rewards, game_info = self.ta_env.close()
            # TextArena's Crosswords already returns a reward in [0, 1] (1.0 on a
            # completed puzzle, otherwise a continuous filled_letter_cells /
            # total_letter_cells fraction), so pass it through unchanged rather
            # than remapping an already-normalised value through (raw + 1) / 2,
            # which compressed every outcome into [0.5, 1.0] and paid a fully
            # failed attempt 0.5.
            reward = rewards.get(0, 0.0) if isinstance(rewards, dict) else float(rewards)

            reason = ""
            if isinstance(game_info, dict) and 0 in game_info:
                reason = game_info[0].get("reason", "")

            summary = f"Game Over! Reward: {reward:.2f}"
            if reason:
                summary += f"\n{reason}"

            return ToolOutput(
                blocks=[TextBlock(text=summary)],
                metadata={"turn": self.turn_count, "reward": reward},
                reward=reward,
                finished=True
            )

        _, obs = self.ta_env.get_observation()
        obs_text = self._format_observation(obs)

        return ToolOutput(
            blocks=[TextBlock(text=obs_text)],
            metadata={"turn": self.turn_count},
            reward=0.0,
            finished=False
        )
