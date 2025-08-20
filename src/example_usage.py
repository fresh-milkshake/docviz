import asyncio

import docviz


async def simple_example():
    document = docviz.Document(r"examples\data\2507.21509v1.pdf")

    extractions = await document.extract_content(
        extraction_config=docviz.ExtractionConfig(page_limit=3),
    )
    extractions.save(document.name, save_format=docviz.SaveFormat.JSON)


async def url_example():
    try:
        document = docviz.Document("https://arxiv.org/pdf/2401.00123.pdf")

        extractions = await document.extract_content(
            extraction_config=docviz.ExtractionConfig(page_limit=3),
            includes=[docviz.ExtractionType.TEXT],
        )
        extractions.save(document.name, save_format=docviz.SaveFormat.XML)

    except Exception as e:
        print(f"Error: {e}")


async def main():
    await simple_example()
    await url_example()


if __name__ == "__main__":
    asyncio.run(main())
