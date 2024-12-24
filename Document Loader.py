from langchain_community.document_loaders import DirectoryLoader
data_path="Dataset"

def doc_loader():
    loader = DirectoryLoader(data_path, glob="*.csv")
    documents = loader.load()
    return documents