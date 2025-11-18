from langchain.embeddings import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

text = "Hello, how are you?"

embedding = embeddings.embed_query(text)

print(embedding)