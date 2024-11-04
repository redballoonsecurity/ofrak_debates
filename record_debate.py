import argparse

from ofrak import *
from ofrak.core import *

from gradio_client import Client, handle_file 
from pydub import AudioSegment
async def gradio_get_ai_voice(output_name: str,text: str, ref_voice_dir: str):
    """
    Generate an ai voice with the F5-TTS gradio app.

    :param text: The text for the model to generate.
    :param ref_voice_dir: The path to the refrence voice, mp3 or wav.
    """
    client = Client("http://0.0.0.0:7860") # Local url to the gradio instance.
    
    result=client.predict(
    ref_audio_orig=handle_file(ref_voice_dir),
    ref_text="", # set to manually define the text in the refrence audio
    gen_text=text,
    model="F5-TTS", # F5-TTS is the only real model you can use.
    remove_silence=False, # Remove silence between batches the model generates.
    cross_fade_duration=0.15, # Fade in for the time between batches the model generates.
    speed=1, # speed of the output afaik
    api_name="/infer"
    )
    wav_data = open(mode="rb",file=result[0]).read()
    seg=AudioSegment.from_wav(BytesIO(wav_data))
    seg.export(out_f = output_name, format="wav")

    # USAGE: await gradio_get_ai_voice(f"Harris {i}.wav",harris_raw.decode(), "path/to/wav/file.wav")

async def main(ofrak_context: OFRAKContext, debate_archive_path: str):
    root_resource = await ofrak_context.create_root_resource_from_file(
        debate_archive_path
    )
    await root_resource.unpack_recursively()
    zip_archive = await root_resource.view_as(ZipArchive)
    for i,question_path in enumerate(await zip_archive.list_dir()):
        question = await zip_archive.get_entry(question_path)
        question_dir = await question.resource.view_as(Folder)
        print(question_dir)
        print("QUESTION")
        question = await question_dir.get_entry("question")
        question_raw = await question.resource.get_data()
        print(question_raw.decode(), end="\n\n")
        await gradio_get_ai_voice(f"Question {i}/Moderator.wav",question_raw.decode(), "voices/Ang_Cui.wav")

        print("=====TRUMP RESPONSE=====")
        trump_answer = await question_dir.get_entry("trump_answer")
        trump_raw = await trump_answer.resource.get_data()
        print(trump_raw.decode(), end="\n\n")
        print("=====GENERATING TRUMP WAV======")
        await gradio_get_ai_voice(f"Question {i}/Trump.wav",trump_raw.decode(), "voices/Donald_Trump.wav")

        print("=====HARRIS RESPONSE=====")
        harris_answer = await question_dir.get_entry("harris_answer")
        harris_raw = await harris_answer.resource.get_data()
        print(harris_raw.decode(), end="\n\n")
        print("=====GENERATING HARRIS WAV======")
        await gradio_get_ai_voice(f"Question {i}/Harris.wav",harris_raw.decode(), "voices/Kamala_Harris.wav")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--debate-archive")
    args = parser.parse_args()

    ofrak = OFRAK()
    ofrak.run(main, args.debate_archive)
