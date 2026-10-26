import asyncio
import json

from app.agents.graph import agent_graph


async def main():
    questions = [
        "Why is my Kubernetes pod in CrashLoopBackOff?",
        "List all available operational runbooks.",
        "What is the company's annual revenue?",
    ]

    for question in questions:
        print("\n" + "=" * 60)
        print("Question:", question)

        try:
            result = await agent_graph.ainvoke({"question": question})

            print(
                json.dumps(
                    result,
                    indent=2,
                    default=str,
                )
            )

        except Exception as exc:
            import traceback

            print(
                "Agent failed:",
                type(exc).__name__,
            )
            print(f"Error details: {exc}")

            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
