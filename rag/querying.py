import json
import boto3
from pinecone import Pinecone
import uuid
from dotenv import load_dotenv


aws_access_key_id = load_dotenv("aws_access_key_id")
aws_secret_access_key = load_dotenv("aws_secret_access_key")
aws_region = "us-east-1"

# Initialize Pinecone connection
pc = Pinecone(api_key="pcsk_5pEARi_DNbj63Mj7ABLU113t4z64p68KZeFwK5UoYMvRHzjWcGycbb3PUi5WNE1LsZ76vs")

# Initialize Bedrock client
bedrock = boto3.client(service_name='bedrock-runtime', region_name='us-east-1')

# Pinecone index name
index_name = "farmcredit"
index = pc.Index(index_name)

# Model IDs
embedding_model_id = "amazon.titan-embed-text-v2:0"
generation_model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0"

def retrieve_similar_chunks(query, top_k=5, bedrock=bedrock, embedding_model_id=embedding_model_id, index=index):
    """
    Embeds the query using Bedrock and retrieves the top_k most similar chunks from Pinecone.

    Args:
        query (str): The user query to search for.
        top_k (int): Number of similar chunks to retrieve (default: 5).
        bedrock (boto3.client): Bedrock client for embedding.
        embedding_model_id (str): Bedrock model ID for embedding.
        index (pinecone.Index): Pinecone index to query.

    Returns:
        list: List of dictionaries containing the top_k chunks with their metadata and scores.
    """
    try:
        # Prepare the input for embedding
        input_data = {
            "inputText": query,
            "dimensions": 512,
            "normalize": True
        }

        # Serialize to JSON
        body = json.dumps(input_data).encode('utf-8')

        # Generate query embedding using Bedrock
        response = bedrock.invoke_model(
            modelId=embedding_model_id,
            contentType="application/json",
            accept="*/*",
            body=body
        )

        response_body = response['body'].read()
        response_json = json.loads(response_body)
        query_embedding = response_json['embedding']

        # Query Pinecone for top_k similar chunks
        query_results = index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )

        # Format results as a list of dictionaries
        retrieved_chunks = [
            {
                "id": match["id"],
                "score": match["score"],
                "question": match["metadata"]["question"],
                "answer": match["metadata"]["answer"]
            }
            for match in query_results["matches"]
        ]

        return retrieved_chunks

    except Exception as e:
        print(f"Error retrieving chunks: {e}")
        raise

def generate_answer(query, retrieved_chunks, bedrock=bedrock, generation_model_id=generation_model_id):
    """
    Generates a final answer using Bedrock based on the query and retrieved chunks.

    Args:
        query (str): The user query.
        retrieved_chunks (list): List of retrieved chunks with metadata.
        bedrock (boto3.client): Bedrock client for text generation.
        generation_model_id (str): Bedrock model ID for text generation.

    Returns:
        str: The generated answer.
    """
    try:
        # Format the context from retrieved chunks
        context = "\n\n".join(
            f"Q: {chunk['question']}\nA: {chunk['answer']}"
            for chunk in retrieved_chunks
        )

        # Create the prompt for the generation model
        prompt = f"""You are a helpful assistant for FarmCredit, a platform supporting Nigerian youth farmers. Use the following context to answer the user's query concisely and accurately. If the context doesn't fully address the query, provide a general response based on FarmCredit's mission and services.

        You are to response as FarmCredit, Do not mention that you are an AI model and do not say that you got the information from the context.
Context:
{context}

Query: {query}

Answer:"""

        # Prepare the input for Bedrock text generation
        input_data = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 500,
            "temperature": 0.7,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }

        # Serialize to JSON
        body = json.dumps(input_data).encode('utf-8')

        # Invoke Bedrock for text generation
        response = bedrock.invoke_model(
            modelId=generation_model_id,
            contentType="application/json",
            accept="*/*",
            body=body
        )

        response_body = response['body'].read()
        response_json = json.loads(response_body)

        # Extract the generated answer
        answer = response_json['content'][0]['text']

        return answer.strip()

    except Exception as e:
        print(f"Error generating answer: {e}")
        raise

def rag_pipeline(query):
    """
    Combines retrieval and generation to answer a query.

    Args:
        query (str): The user query.

    Returns:
        str: The final generated answer.
    """
    try:
        # Retrieve top 5 similar chunks
        retrieved_chunks = retrieve_similar_chunks(query, top_k=5)
        # Generate answer using retrieved chunks
        answer = generate_answer(query, retrieved_chunks)
        return answer
    except Exception as e:
        print(f"Error in RAG pipeline: {e}")
        return "Sorry, an error occurred while processing your query. Please try again."


#print(rag_pipeline("Hi there, Describe you in 5 words?"))
