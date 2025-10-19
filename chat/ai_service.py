# chat/ai_service.py
import os
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import DocArrayInMemorySearch
from langchain_core.prompts import PromptTemplate
from operator import itemgetter
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from django.conf import settings

class CintraconAIService:
    def __init__(self):
        self.openai_api_key = settings.OPENAI_API_KEY
        self.pdf_file_path = settings.PDF_FILE_PATH
        self.model = None
        self.embeddings = None
        self.chain = None
        self._initialize_ai()

    def _initialize_ai(self):
        """Initialize AI model and chain"""
        try:
            # Check if PDF file exists
            if not os.path.exists(self.pdf_file_path):
                print(f"PDF file not found at: {self.pdf_file_path}")
                self._create_fallback_chain()
                return

            # Initialize model and embeddings using your test code structure
            self.model = ChatOpenAI(
                model_name="gpt-4",  # Using gpt-4 as in your test code
                openai_api_key=self.openai_api_key,
                temperature=0.7
            )
            self.embeddings = OpenAIEmbeddings(openai_api_key=self.openai_api_key)
            
            # Load and split the PDF into pages (same as your test code)
            loader = PyPDFLoader(self.pdf_file_path)
            pages = loader.load_and_split()

            # Create in-memory vector store from the PDF pages
            vectorstore = DocArrayInMemorySearch.from_documents(pages, embedding=self.embeddings)
            retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

            # Define the prompt template (improved version of your test code)
            template = """
            You are Cintracon AI Assistant. Answer the question based on the context below and must reply with specific answers. 
            Don't reply all answers at a time. 
            
            Language Guidelines:
            - If question is in English, respond in English
            - If question is in Bangla (বাংলা), respond in Bangla
            - If question is in Banglish (Romanized Bengali), respond in Bangla with proper Bengali script
            - If you can't answer the question based on context, reply "I don't know"
            
            Context: {context}

            Question: {question}
            
            Answer: """
            
            prompt = PromptTemplate.from_template(template)

            # Create composite chain (same structure as your test code)
            self.chain = (
                {
                    "context": itemgetter("question") | retriever,
                    "question": itemgetter("question"),
                }
                | prompt
                | self.model
                | StrOutputParser()
            )
            
            print("✅ AI Service initialized successfully with PDF!")
            
        except Exception as e:
            print(f"❌ AI initialization error: {e}")
            self._create_fallback_chain()

    def _create_fallback_chain(self):
        """Create a fallback chain without PDF for basic functionality"""
        try:
            print("🔄 Creating fallback AI chain...")
            
            self.model = ChatOpenAI(
                model_name="gpt-4",
                openai_api_key=self.openai_api_key,
                temperature=0.7
            )
            
            # Simple chain without PDF context
            template = """
            You are Cintracon AI Assistant. You help students with educational content.
            
            Language Guidelines:
            - If question is in English, respond in English
            - If question is in Bangla (বাংলা), respond in Bangla  
            - If question is in Banglish (Romanized Bengali), respond in Bangla with proper Bengali script
            
            Question: {question}
            
            Provide helpful educational response: """
            
            prompt = PromptTemplate.from_template(template)
            
            self.chain = (
                {"question": RunnablePassthrough()}
                | prompt
                | self.model
                | StrOutputParser()
            )
            
            print("✅ Fallback AI chain created!")
            
        except Exception as e:
            print(f"❌ Fallback chain creation failed: {e}")
            self.chain = None

    def get_ai_response(self, question):
        """Get AI response for a question"""
        if not self.chain:
            return "AI service is currently unavailable. Please try again later."
        
        try:
            # Use the same input format as your test code
            question_input = {"question": question}
            response = self.chain.invoke(question_input)
            return response.strip()
            
        except Exception as e:
            print(f"❌ AI response error: {e}")
            # Fallback response
            return "I apologize, but I'm having trouble processing your request right now. Please try again later."

# Global instance
ai_service = CintraconAIService()