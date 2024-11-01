import argparse

from ofrak import *
from ofrak.core import *


async def main(ofrak_context: OFRAKContext, debate_archive_path: str):
    root_resource = await ofrak_context.create_root_resource_from_file(
        debate_archive_path
    )
    await root_resource.unpack_recursively()
    zip_archive = await root_resource.view_as(ZipArchive)
    for question_path in await zip_archive.list_dir():
        question = await zip_archive.get_entry(question_path)
        question_dir = await question.resource.view_as(Folder)
        print(question_dir)
        print("QUESTION")
        question = await question_dir.get_entry("question")
        question_text = await question.resource.get_data()
        print(question_text.decode(), end="\n\n")

        print("=====TRUMP RESPONSE=====")
        trump_answer = await question_dir.get_entry("trump_answer")
        trump_raw = await trump_answer.resource.get_data()
        print(trump_raw.decode(), end="\n\n")

        print("=====HARRIS RESPONSE=====")
        harris_answer = await question_dir.get_entry("harris_answer")
        harris_raw = await harris_answer.resource.get_data()
        print(harris_raw.decode(), end="\n\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--debate-archive")
    args = parser.parse_args()

    ofrak = OFRAK()
    ofrak.run(main, args.debate_archive)
