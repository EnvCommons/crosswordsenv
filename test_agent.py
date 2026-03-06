import asyncio
import json
import os
from openai import AsyncOpenAI
from openreward import AsyncOpenReward


async def test_with_openai():
    or_client = AsyncOpenReward()
    oai_client = AsyncOpenAI()

    MODEL_NAME = "gpt-5.2"
    ENV_NAME = "crosswordsenvironment"
    SPLIT = "test"
    BASE_URL = "http://localhost:8080"

    environment = or_client.environments.get(name=ENV_NAME, base_url=BASE_URL)
    tasks = await environment.list_tasks(split=SPLIT)

    # Define tools manually (since we're testing locally)
    tools = [
        {
            "type": "function",
            "name": "place_letter",
            "description": "Place a letter on the crossword grid at the given row and column (0-indexed).",
            "parameters": {
                "type": "object",
                "properties": {
                    "row": {
                        "type": "integer",
                        "description": "Row index (0-indexed)"
                    },
                    "column": {
                        "type": "integer",
                        "description": "Column index (0-indexed)"
                    },
                    "letter": {
                        "type": "string",
                        "description": "Single letter a-z"
                    }
                },
                "required": ["row", "column", "letter"],
                "additionalProperties": False
            }
        }
    ]

    print(f"Found {len(tasks)} tasks")

    # Test first task only
    for task in tasks[:1]:
        print(f"\nTesting task: {task['id']}")

        async with environment.session(task=task) as session:
            prompt = await session.get_prompt()
            input_list = [{"role": "user", "content": prompt[0].text}]
            finished = False
            turn_count = 0
            max_turns = 100  # Limit turns to prevent infinite loops

            while not finished and turn_count < max_turns:
                turn_count += 1

                # Use responses.create(), NOT chat.completions.create()
                response = await oai_client.responses.create(
                    model=MODEL_NAME,
                    tools=tools,
                    input=input_list
                )

                # Response has 'output', NOT 'choices'
                input_list += response.output

                for item in response.output:
                    if item.type == "function_call":
                        print(f"\nTurn {turn_count}: Calling {item.name} with {item.arguments}")

                        tool_result = await session.call_tool(
                            item.name,
                            json.loads(str(item.arguments))
                        )

                        finished = tool_result.finished

                        input_list.append({
                            "type": "function_call_output",
                            "call_id": item.call_id,
                            "output": tool_result.blocks[0].text
                        })

                        print(f"Reward: {tool_result.reward:.3f}")

                        if tool_result.finished:
                            print('\nGAME FINISHED!')
                            print(f"Final reward: {tool_result.reward:.3f}")
                            break

            if turn_count >= max_turns:
                print(f"\nReached max turns ({max_turns})")


if __name__ == "__main__":
    asyncio.run(test_with_openai())
