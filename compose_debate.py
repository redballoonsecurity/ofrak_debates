import textwrap

from ofrak import *
from ofrak.core import *
from ofrak.core.llm import *


async def main(ofrak_context: OFRAKContext):
    root_resource = await ofrak_context.create_root_resource(
        name="November 2024 Fake Debate",
        data=b"",
        tags=(FilesystemRoot,),
    )
    filesystem_view = await root_resource.view_as(FilesystemRoot)

    for i in range(1, 3):
        child = await filesystem_view.add_file(
            f"question_{i}/question",
            data=b"",
        )
        await child.run(
            LlmAnalyzer,
            LlmAnalyzerConfig(
                api_url="http://localhost:11434/api/chat",
                model="llama3.2",
                prompt="Ask a question of the presidential candidate. Do not explain why you asked the question, simply ask the question. Do not address a specific person when asking the question",
                system_prompt="You are a moderator for the 2024 US Presidential Debate.",
            ),
        )
        question = child.get_attributes(LlmAttributes).description
        await child.run(
            BinaryExtendModifier, BinaryExtendConfig(wrap_text(question).encode())
        )
        await child.identify()

        # Harris Resposne
        harris_answer = await filesystem_view.add_file(
            f"question_{i}/harris_answer",
            data=b"",
        )
        await harris_answer.run(
            LlmAnalyzer,
            LlmAnalyzerConfig(
                api_url="http://localhost:11434/api/chat",
                model="llama3.2",
                prompt=question,
                system_prompt="You are an actor playing Kamala Harris in a presidential debate. Do not break character.",
            ),
        )
        await harris_answer.run(
            BinaryExtendModifier,
            BinaryExtendConfig(
                wrap_text(
                    harris_answer.get_attributes(LlmAttributes).description
                ).encode()
            ),
        )
        await harris_answer.identify()

        # Trump Response
        trump_answer = await filesystem_view.add_file(
            f"question_{i}/trump_answer",
            data=b"",
        )
        await trump_answer.run(
            LlmAnalyzer,
            LlmAnalyzerConfig(
                api_url="http://localhost:11434/api/chat",
                model="llama3.2",
                prompt=question,
                system_prompt="You are an actor playing  Donald Trump in a presidential debate. Do not break character.",
            ),
        )
        await trump_answer.run(
            BinaryExtendModifier,
            BinaryExtendConfig(
                wrap_text(
                    trump_answer.get_attributes(LlmAttributes).description
                ).encode()
            ),
        )
        await trump_answer.identify()

    # server = await open_gui("127.0.0.1", 8081, focus_resource=root_resource, ofrak_context=ofrak_context, open_in_browser=True)
    # await server.run_until_cancelled()

    root_resource.add_tag(ZipArchive)
    await root_resource.save()
    await root_resource.pack()
    await root_resource.flush_data_to_disk(f"ofrak_debate_2024.zip")


def wrap_text(text: str):
    return "\n\n".join(textwrap.fill(para) for para in text.split("\n\n"))


if __name__ == "__main__":
    ofrak = OFRAK()
    ofrak.run(main)
