from rag.retriever import retrieve

query = input("Query> ")

result = retrieve(
    query,
    top_k=10
)

print(result)