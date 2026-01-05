import asyncio
import json
import random
import websockets


async def handler(websocket):
    """
    Fake Raspberry Pi backend.
    Sends instruction updates and final result as JSON.
    """

    progress = 0

    try:
        while True:
            # Instruction phase
            instruction_msg = {
                "type": "instruction",
                "text": random.choice([
                    "Move palm closer",
                    "Hold steady",
                    "Tilt left",
                    "Tilt right"
                ]),
                "distance_cm": round(random.uniform(6.0, 20.0), 1),
                "state": random.choice([
                    "TOO_FAR",
                    "TOO_CLOSE",
                    "PERFECT",
                    "CAPTURING",
                    "PROCESSING"
                ]),
                "mode": "registration",
                "tilt": random.choice(["LEFT", "STRAIGHT", "RIGHT"]),
                "progress": progress,
                "confidence": None
            }

            await websocket.send(json.dumps(instruction_msg))

            progress += 10

            # Final result
            if progress >= 100:
                result_msg = {
                    "type": "result",
                    "text": random.choice(["MATCH", "NO MATCH"]),
                    "distance_cm": 8.4,
                    "state": "PERFECT",
                    "mode": "matching",
                    "tilt": "STRAIGHT",
                    "progress": 100,
                    "confidence": round(random.uniform(70, 98), 1)
                }

                await websocket.send(json.dumps(result_msg))
                progress = 0

            await asyncio.sleep(1)

    except websockets.exceptions.ConnectionClosed:
        print("GUI disconnected")


async def main():
    print("Fake backend running on ws://localhost:8765")
    async with websockets.serve(handler, "localhost", 8765):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
