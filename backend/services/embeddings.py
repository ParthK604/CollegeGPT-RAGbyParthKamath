from sentence_transformers import SentenceTransformer
class EmbeddingService:
    def __init__(self,model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
    def embed_chunks(self, chunks):
        texts = [chunk.page_content for chunk in chunks]
        embeddings = self.model.encode(texts,show_progress_bar=True)

        return embeddings
    def embed_query(self, query: str):

        return self.model.encode(
            query,
            convert_to_numpy=True
        )
    
