
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings,ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate
from langchain.schema import Document
from langchain_core.output_parsers import StrOutputParser

from langchain.schema.runnable import RunnableParallel,RunnableLambda, RunnablePassthrough

MODEL_VERSION  = 1.0


def build_vector_store(transcript_list):
    ####1.Indexing
    #Building vector database
    docs = []
    for snippet in transcript_list:
        docs.append(Document(
            page_content= snippet.text,
            metadata = {'start':snippet.start}
            ))
    
    splitter = RecursiveCharacterTextSplitter(chunk_size=500,chunk_overlap = 100)
    chunks = splitter.split_documents(documents=docs)

    #creating vector store
    embedding_model = OpenAIEmbeddings()
    vector_store = FAISS.from_documents(
        documents=chunks,
        embedding=embedding_model
    )

    return vector_store


def context_builder(retieved_docs):
    context_text = "\n\n".join(doc.page_content for doc in retieved_docs)
    return context_text


def rag(transcript_list,question):

    #build vector store
    vector_store = build_vector_store(transcript_list)
    
    ####2.Retrieval
    retriever = vector_store.as_retriever(
    search_type = 'mmr',
    search_kwargs = {
        'fetch_k':10,
        'k':4,
        'lambda_multi':0.5}
        )

    #building context with time stamp
    retrieved_docs = retriever.invoke(input=question)
    timestamp_context = []
    
    for doc in retrieved_docs:
        timestamp = doc.metadata.get('start',0) 
        timestamp_context.append({
            'text':doc.page_content,
            'timestamp':timestamp
        })

    ####3.Augumentation
    #3.1 Build Prompt
    prompt = PromptTemplate(
        template="""
        You are a helpful assistant.
        Answer ONLY from the provided transcript context.
        If the context is insufficient, just say you don't know.

        {context}
        Question: {question}
        """,
        input_variables = ['context', 'question']
    )


    #Generation
    model = ChatOpenAI(model='gpt-4.1-mini-2025-04-14')
    parser = StrOutputParser()

    prompt_chain = RunnableParallel({
        'context': retriever | RunnableLambda(context_builder),
        'question' : RunnablePassthrough()
    })

    final_chain = prompt_chain | prompt | model | parser
    try:
        llm_response = final_chain.invoke(question)
    except Exception as e:
        print('####### Exception Occured#######',str(e))

    return timestamp_context,llm_response


