import json
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

    question_resource = await ofrak_context.create_root_resource("", b"")
    await question_resource.run(
        LlmAnalyzer,
        LlmAnalyzerConfig(
            api_url="http://localhost:11434/api/chat",
            model="llama3.2",
            prompt="Ask ten questions of the presidential candidate. Do not explain why you asked the question, simply ask the question. Do not address a specific person when asking the question. Ask one question on each line.",
            system_prompt="You are a moderator for the 2024 US Presidential Debate.",
        ),
    )
    all_questions = question_resource.get_attributes(LlmAttributes).description
    questions = [q.strip() for q in all_questions.splitlines() if q]
    for i, question in enumerate(questions):
        child = await filesystem_view.add_file(
            f"question_{i + 1}/question",
            data=b"",
        )
        await child.run(
            BinaryExtendModifier, BinaryExtendConfig(wrap_text(question).encode())
        )

        # Harris Resposne
        harris_answer = await filesystem_view.add_file(
            f"question_{i + 1}/harris_answer",
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
            f"question_{i + 1}/trump_answer",
            data=b"",
        )
        await trump_answer.run(
            LlmAnalyzer,
            LlmAnalyzerConfig(
                api_url="http://localhost:11434/api/chat",
                model="llama3.2",
                prompt=question,
                system_prompt="You are an actor playing Donald Trump in a presidential debate. Do not break character.",
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

    root_resource.add_tag(ZipArchive)
    await root_resource.save()
    await root_resource.pack()
    await root_resource.flush_data_to_disk(f"ofrak_debate_2024.zip")


def wrap_text(text: str):
    return "\n\n".join(textwrap.fill(para) for para in text.split("\n\n"))


if __name__ == "__main__":
    ofrak = OFRAK()
    ofrak.run(main)
