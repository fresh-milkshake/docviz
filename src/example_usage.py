# variant 1
import asyncio

import docviz


async def main():
    document = docviz.Document(r"examples\data\2507.21509v1.pdf")

    extractions = await document.extract_content()
    extractions.save("results", save_format=docviz.SaveFormat.JSON)


asyncio.run(main())


# # variant 1
# import docviz


# document = docviz.Document("data\2507.21509v1.pdf")

# extractions = document.extract_content_sync()
# extractions.save("results.json", save_format=docviz.SaveFormat.JSON)

# # variant 2 - Batch processing multiple documents
# import docviz
# import os
# from pathlib import Path

# # Process all PDF files in a directory
# pdf_directory = Path("data/papers/")
# output_dir = Path("output/")
# output_dir.mkdir(exist_ok=True)
# pdfs = pdf_directory.glob("*.pdf")

# documents = [docviz.Document(str(pdf)) for pdf in pdfs]
# extractions = docviz.batch_extract(documents)

# for ext in extractions:
#     ext.save(
#         output_dir, save_format=[docviz.SaveFormat.JSON, docviz.SaveFormat.CSV]
#     )

# # variant 5 - Selective extraction with filters
# import docviz

# document = docviz.Document("data\2507.21509v1.pdf")

# # Extract only specific types of content
# extractions = document.extract_content(
#     includes=[
#         docviz.ExtractionType.TABLE,
#         docviz.ExtractionType.TEXT,
#         docviz.ExtractionType.FIGURE,
#         docviz.ExtractionType.EQUATION,
#     ]
# )

# extractions.save("selective_results.json", save_format=docviz.SaveFormat.JSON)

# # variant 6 - Processing with custom configuration
# import docviz

# # Configure extraction settings
# config = docviz.ExtractionConfig(
#     extraction_type=docviz.ExtractionType.ALL,
#     extraction_config=docviz.ExtractionConfig(
#         extraction_type=docviz.ExtractionType.ALL,
#     ),
# )

# document = docviz.Document("data\2507.21509v1.pdf", config=config)
# extractions = document.extract_content()
# extractions.save("configured_results.json", save_format=docviz.SaveFormat.JSON)

# # variant 7 - Streaming processing for large documents
# import docviz

# document = docviz.Document("data\large_document.pdf")

# # Process document in chunks to save memory
# for chunk in document.extract_streaming(chunk_size=10):
#     # Process each chunk (10 pages at a time)
#     chunk.save(f"chunk_{chunk.page_range}.json", save_format=docviz.SaveFormat.JSON)

# # variant 8 - Interactive extraction with progress tracking
# import docviz
# from tqdm import tqdm

# document = docviz.Document("data\2507.21509v1.pdf")

# # Extract with progress bar
# with tqdm(total=document.page_count, desc="Extracting content") as pbar:
#     extractions = document.extract_content(progress_callback=pbar.update)

# extractions.save("progress_results.json", save_format=docviz.SaveFormat.JSON)

# # variant 10 - Custom output formatting
# import docviz
# import json

# document = docviz.Document("data\2507.21509v1.pdf")
# extractions = document.extract_content()

# # Custom JSON formatting with metadata
# output_data = {
#     "metadata": {
#         "source_file": "data\2507.21509v1.pdf",
#         "extraction_date": "2024-01-15",
#         "version": "1.0",
#     },
#     "content": extractions.to_dict(),
# }

# with open("custom_formatted.json", "w", encoding="utf-8") as f:
#     json.dump(output_data, f, indent=2, ensure_ascii=False)


# # variant 12 - Integration with data analysis pipeline
# import docviz
# import pandas as pd
# import matplotlib.pyplot as plt

# document = docviz.Document("data\2507.21509v1.pdf")
# extractions = document.extract_content()

# # Convert to pandas DataFrame for analysis
# df = extractions.to_dataframe()

# # Basic analysis
# print(f"Total tables extracted: {len(df[df['type'] == 'table'])}")
# print(f"Total figures extracted: {len(df[df['type'] == 'figure'])}")

# # Save as Excel with multiple sheets
# with pd.ExcelWriter("analysis_results.xlsx") as writer:
#     df.to_excel(writer, sheet_name="All_Content", index=False)

#     # Separate sheets by content type
#     for content_type in df["type"].unique():
#         type_df = df[df["type"] == content_type]
#         type_df.to_excel(writer, sheet_name=f"{content_type.capitalize()}", index=False)
