from app.services.vector_db_service import VectorDBService

class RetrievalService:
    def __init__(self):
        self.vector_db = VectorDBService()
        # Create a retriever interface from the vector store
        self.retriever = self.vector_db.get_vector_store().as_retriever(
            search_type="similarity",
            # k=4 means we retrieve the top 4 most relevant chunks
            search_kwargs={"k": 4} 
        )

    def retrieve_context(self, query: str):
        """
        Performs a semantic similarity search to find relevant document chunks
        matching the user's query.
        """
        docs = self.retriever.invoke(query)
        return docs
