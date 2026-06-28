import asyncio
import edge_tts


async def _synthesize(text: str, voice: str = "en-US-GuyNeural") -> bytes:
    communicate = edge_tts.Communicate(text, voice)
    audio = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio += chunk["data"]
    return audio


def synthesize(text: str) -> bytes:
    return asyncio.run(_synthesize(text))
