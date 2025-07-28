import fitz 
import json
import os
import torch
from sentence_transformers import SentenceTransformer, util
import datetime

INPUT_DIR = '/app/input'
PDF_DIR = os.path.join(INPUT_DIR, 'pdfs')
OUTPUT_DIR = '/app/output'
MODEL_CACHE_DIR = '/app/models_cache'
DEVICE = "cpu"

CONFIG_FILE_PATH = None
for f in os.listdir(INPUT_DIR):
    if f.endswith('.json'):
        CONFIG_FILE_PATH = os.path.join(INPUT_DIR, f)
        break

def load_model(model_name='all-MiniLM-L6-v2'):
    print(f"Loading model {model_name} onto {DEVICE}...")
    model = SentenceTransformer(model_name, cache_folder=MODEL_CACHE_DIR)
    model.to(DEVICE)
    print("Model loaded successfully.")
    return model

def extract_text_chunks(pdf_path):
    if not os.path.exists(pdf_path):
        print(f"Warning: PDF file not found at {pdf_path}. Skipping.")
        return []
    doc = fitz.open(pdf_path)
    chunks = []
    for page_num, page in enumerate(doc):
        blocks = page.get_text("blocks")
        for i, b in enumerate(blocks):
            text = b[4].strip()
            if len(text.split()) > 10:
                chunks.append({
                    "document": os.path.basename(pdf_path),
                    "page_number": page_num + 1,
                    "text": text,
                    "section_title": f"Page {page_num + 1}, Block {i+1}"
                })
    return chunks

def analyze_documents_for_persona(doc_collection, persona, job_to_be_done, model):
    query = f"Persona: {persona}. Task: {job_to_be_done}"
    print(f"\nAnalyzing for query: {query}")
    query_embedding = model.encode(query, convert_to_tensor=True, device=DEVICE)

    all_chunks = []
    for doc_path in doc_collection:
        print(f"Extracting text from {doc_path}...")
        all_chunks.extend(extract_text_chunks(doc_path))

    if not all_chunks:
        print("No text could be extracted from the documents.")
        return [], []

    print(f"Encoding {len(all_chunks)} text chunks...")
    corpus_texts = [chunk['text'] for chunk in all_chunks]
    corpus_embeddings = model.encode(corpus_texts, convert_to_tensor=True, device=DEVICE, show_progress_bar=True)

    print("Calculating relevance scores...")
    cosine_scores = util.pytorch_cos_sim(query_embedding, corpus_embeddings)[0]
    ranked_chunks = sorted(zip(cosine_scores, all_chunks), key=lambda x: x[0], reverse=True)

    extracted_sections, sub_section_analysis = [], []
    for i, (score, chunk) in enumerate(ranked_chunks):
        if score > 0.2:
            extracted_sections.append({
                "document": chunk["document"],
                "page_number": chunk["page_number"],
                "section_title": chunk["section_title"],
                "importance_rank": i + 1
            })
            sub_section_analysis.append({
                "document": chunk["document"],
                "page_number": chunk["page_number"],
                "refined_text": chunk["text"],
                "relevance_score": float(score)
            })
    return extracted_sections, sub_section_analysis

def create_output_json(doc_paths, persona, job, sections, subsections, output_path):
    output_data = {
        "metadata": {
            "input_documents": [os.path.basename(p) for p in doc_paths],
            "persona": persona,
            "job_to_be_done": job,
            "processing_timestamp": datetime.datetime.now().isoformat()
        },
        "extracted_sections": sections,
        "sub_section_analysis": subsections
    }
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=4, ensure_ascii=False)
    print(f"\nOutput saved to {output_path}")

if __name__ == '__main__':
    if not CONFIG_FILE_PATH or not os.path.exists(CONFIG_FILE_PATH):
        raise FileNotFoundError(f"Configuration JSON file not found in {INPUT_DIR}")

    with open(CONFIG_FILE_PATH, 'r') as f:
        config = json.load(f)

    PERSONA_DEFINITION = config.get("persona", {}).get("role")
    JOB_TO_BE_DONE = config.get("job_to_be_done", {}).get("task")

    if not PERSONA_DEFINITION or not JOB_TO_BE_DONE:
        raise ValueError("Persona 'role' and Job 'task' must be defined in the input JSON")

    documents_to_process = config.get("documents", [])
    if not documents_to_process:
        raise ValueError("No documents listed in the input JSON file.")

    document_collection = [os.path.join(PDF_DIR, doc['filename']) for doc in documents_to_process]

    if not document_collection:
        print("No PDF documents found to process.")
    else:
        model = load_model()
        extracted, subsections = analyze_documents_for_persona(
            document_collection, PERSONA_DEFINITION, JOB_TO_BE_DONE, model
        )
        output_json_path = os.path.join(OUTPUT_DIR, 'challenge1b_output.json')
        create_output_json(
            document_collection, PERSONA_DEFINITION, JOB_TO_BE_DONE, extracted, subsections, output_json_path
        )
