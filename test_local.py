import asyncio
from openreward import AsyncOpenReward


async def test_locally():
    client = AsyncOpenReward()

    # Connect to local server
    env = client.environments.get(
        name="crosswordsenvironment",
        base_url="http://localhost:8080"
    )

    # Get tasks
    tasks = await env.list_tasks(split="test")
    print(f"Found {len(tasks)} tasks")

    example_task = tasks[0]
    print(f"Testing task: {example_task.id if hasattr(example_task, 'id') else example_task}")

    # Test with session
    async with env.session(task=example_task) as session:
        # Test prompt generation
        prompt = await session.get_prompt()
        print(f"\n{'='*60}")
        print("PROMPT:")
        print(f"{'='*60}")
        print(f"{prompt[0].text[:500]}...")
        print(f"{'='*60}\n")

        # Test tool call - place letter 'a' at row 0, column 0
        print("Testing place_letter(row=0, column=0, letter='a')...")
        result = await session.call_tool("place_letter", {
            "row": 0,
            "column": 0,
            "letter": "a"
        })

        print(f"\n{'='*60}")
        print("TOOL RESULT:")
        print(f"{'='*60}")
        print(f"Reward: {result.reward}")
        print(f"Finished: {result.finished}")
        print(f"Output: {result.blocks[0].text[:300]}")
        print(f"{'='*60}\n")

        if result.finished:
            print("Game finished on first move!")
        else:
            print("Game continuing after first move (expected)")

        print("\nSMOKE TEST PASSED!")


if __name__ == "__main__":
    asyncio.run(test_locally())
