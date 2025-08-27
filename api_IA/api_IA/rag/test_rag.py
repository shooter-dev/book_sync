import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from api_IA.api_IA.rag.agent import ask_openai
from api_IA.api_IA.rag.vectorizer import encode_text, retrieve_similar_documents


# 1. Ta question
question = "Quels sont les thèmes abordés dans le volume 3 de la série Naruto ?"

# 2. Transformer la question en vecteur
embedding = encode_text(question)

# 3. Chercher les documents les plus proches
results = retrieve_similar_documents(embedding, top_k=5)
documents = [doc["content"] for doc in results]

# 4. Envoyer à OpenAI pour obtenir une réponse
response = ask_openai(question, documents)

# 5. Afficher la réponse
print("Réponse de l'agent :\n")
print(response)
