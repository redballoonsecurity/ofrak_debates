import textwrap
from dataclasses import dataclass

from gradio_client import Client, handle_file
from ofrak.core import *
from ofrak.core.llm import *
from ofrak.model.component_model import CC


@dataclass
class Person(ResourceView):
    name: str
    audio_sample: str


@dataclass
class AnswerQuestionConfig(ComponentConfig):
    question: str
    tts_client_url: str


class AnswerQuestionModifier(Modifier[AnswerQuestionConfig]):
    targets = (Person,)

    async def modify(self, resource: Resource, config: AnswerQuestionConfig):
        """
        Answer question, add it to firmware object, and generate and run a wave file.
        """
        await resource.save()
        person = await resource.view_as(Person)
        print(f"[+] {person.name} considering the question...")
        raw_data = await resource.get_data()
        start_line = len(raw_data.decode().splitlines())
        await resource.run(
            LlmAnalyzer,
            LlmAnalyzerConfig(
                api_url="http://localhost:11434/api/chat",
                model="llama3.2",
                prompt=config.question,
                system_prompt=f"You are an actor playing {person.name} in a presidential debate. Do not break character.",
            ),
        )
        await resource.run(
            BinaryExtendModifier,
            BinaryExtendConfig(
                wrap_text(resource.get_attributes(LlmAttributes).description).encode()
            ),
        )
        print(f"[+] {person.name} generating audio response...")
        await resource.run(
            TTSAnalyzer,
            TTSAnalyzerConfig(start_line=start_line, client_url=config.tts_client_url),
        )
        resource.remove_attributes(LlmAttributes)
        resource.remove_component(LlmAnalyzer.get_id())


@dataclass(**ResourceAttributes.DATACLASS_PARAMS)
class WavFile(ResourceAttributes):
    wav: bytes


@dataclass
class TTSAnalyzerConfig(ComponentConfig):
    start_line: int = 0
    num_lines: int = -1  # If -1, read to end of file
    client_url: str = "http://0.0.0.0:7860"


class TTSAnalyzer(Analyzer[TTSAnalyzerConfig, WavFile]):
    """
    Analyze a binary blob to extract its mimetype and magic description.
    """

    targets = (Person,)
    outputs = (WavFile,)

    async def analyze(
        self, resource: Resource, config: TTSAnalyzerConfig = TTSAnalyzerConfig()
    ) -> WavFile:
        data = await resource.get_data()
        lines = data.decode().splitlines()
        if len(lines) < config.start_line:
            raise ValueError
        if config.num_lines == -1:
            text = "\n".join(lines[config.start_line :])
        else:
            if len(lines) < config.start_line + config.num_lines:
                raise ValueError
            text = "\n".join(
                lines[config.start_line : config.start_line + config.num_lines]
            )

        client = Client(config.client_url)  # Local url to the gradio instance.

        person = await resource.view_as(Person)
        print(f"[+] Converting text to speech for {person.name}...")
        result = client.predict(
            ref_audio_orig=handle_file(person.audio_sample),
            ref_text="",  # set to manually define the text in the refrence audio
            gen_text=text,
            model="F5-TTS",  # F5-TTS is the only real model you can use.
            remove_silence=False,  # Remove silence between batches the model generates.
            cross_fade_duration=0.15,  # Fade in for the time between batches the model generates.
            speed=1,  # speed of the output afaik
            api_name="/infer",
        )
        wav_data = open(mode="rb", file=result[0]).read()
        print(f"[+] Convestion complete")
        return WavFile(wav_data)

    async def _run(self, resource: Resource, config: CC):
        if resource.has_component_run(self.get_id()):
            print("Removing!")
            resource.remove_component(self.get_id())
        await super()._run(resource, config)


def wrap_text(text: str):
    return "\n\n".join(textwrap.fill(para) for para in text.split("\n\n"))
