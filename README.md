# Adobe-India-Connecting-the-Dots-Challenge-2025_1b
**Adobe India Hackathon 2025: Round 1B – Persona-Driven Document Intelligence**

---

## Submission for the "Connecting the Dots" Challenge

This repository contains the complete solution for Round 1B. The mission is to build an intelligent document analyst that extracts and prioritizes the most relevant sections from a collection of documents based on a specific user persona and their "job-to-be-done."

---

## Our Methodology

The challenge of extracting useful information for a specific user persona requires a system that can move beyond simple keyword matching and grasp the underlying semantic meaning of both the user's intent and the document's content. Our methodology achieves this through a lightweight, efficient, and offline-first approach centered on sentence embeddings and vector similarity, ensuring compliance with the strict CPU-only, no-network, and performance constraints of the hackathon.

Our approach is a four-stage pipeline:

### 1. Semantic Query Formulation

The process begins by understanding the user's needs. We combine the provided persona (e.g., "Travel Planner") and the job_to_be_done (e.g., "Plan a trip for college friends") into a single, comprehensive query string. This unified query serves as the ground truth for the user's intent, providing a rich semantic target for our system to search for.

### 2. Granular Text Chunking

Recognizing that relevance often lies within specific paragraphs rather than entire documents, we first parse each PDF in the collection. The text is segmented into coherent, paragraph-level chunks. This granularity is key to providing precise and actionable results. Each chunk is stored along with its source document and page number, maintaining a clear link back to its origin.

### 3. High-Fidelity Semantic Embedding

This is the core of our intelligent system. We utilize the all-MiniLM-L6-v2 sentence-transformer model, a state-of-the-art neural network chosen for its exceptional balance of performance, speed, and small footprint (~90MB). This model is specifically trained to convert text into high-dimensional vector embeddings, where the geometric distance between vectors corresponds to their semantic similarity.

First, the semantic query formulated in stage one is passed through the model to generate a query vector.  
Next, every single text chunk extracted from the documents is passed through the same model, generating a corpus of content vectors.

This process transforms the abstract problem of "finding relevant text" into a concrete mathematical problem of finding vectors that are close to each other.

### 4. Relevance Ranking via Cosine Similarity

With the query and all text chunks represented as vectors in the same high-dimensional space, we can accurately measure their semantic relationship. We compute the cosine similarity between the query vector and every content vector in our corpus. A higher cosine score indicates a stronger semantic match. The text chunks are then sorted in descending order based on this similarity score. The resulting rank directly reflects the semantic relevance of each chunk to the user's persona and task, providing the final, prioritized output.

---

## How to Build and Run

The solution is fully containerized using Docker and is designed to run completely offline. The model and all dependencies are included in the pre-built image available on Docker Hub.  
**Docker Hub Repo:** https://hub.docker.com/r/sidpossibly/round1b-app

---

## Prerequisites

Docker must be installed and running on your system.

---

## Step 1: Prepare Directories and Configuration

In your working directory, create the required input and output folders. The input directory must contain a `PDFs` subfolder and the configuration JSON file (e.g., `challenge1b_input.json`).

```bash
mkdir -p input/PDFs
mkdir output
```

Your directory should look like this:

```plaintext
your-working-directory/
├── input/
│   ├── config.json
│   └── PDFs/
│       └── your-document.pdf
└── output/
```

Place all the PDF files you want to analyze inside the `input/pdfs` folder.

The `config.json` must follow this structure:

```json
{
  "persona": {
    "role": "Your defined user persona"
  },
  "job_to_be_done": {
    "task": "The specific objective the persona wants to achieve"
  },
  "documents": [
    {
      "filename": "your-document.pdf"
    }
  ]
}
```

---

## Step 2: Pull and Run the Docker Container

**Pull the prebuilt Docker image:**

```bash
docker pull sidpossibly/round1b-app
```

**Run the container:**

```bash
docker run --rm \
  -v "$(pwd)/input:/app/input" \
  -v "$(pwd)/output:/app/output" \
  --network none \
  sidpossibly/round1b-app
```

---

## Output

The script will generate a file named `challenge1b_output.json` inside the `output/` directory.  
It contains:
- Extracted sections relevant to the persona's task
- Relevance-scored subsections using sentence embeddings

---

## Notes

- ❌ No internet calls during runtime  
- 📄 Uses clean test PDFs and configuration  
- 🚀 Easy-to-run containers for judges and reviewers

---

## Authors

- **Deon Sajan**  
  B.Tech CSE, Amrita Vishwa Vidyapeetham

- **Sidharth R Krishna**  
  B.Tech CSE, Amrita Vishwa Vidyapeetham

- **Yampathi Sai Sailesh Reddy**  
  B.Tech CSE, Amrita Vishwa Vidyapeetham

---

## Hackathon Submission

**Adobe India – "Connecting the Dots" Challenge 2025**

