# mcp_analyzer.py

import os
import time
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
import openai

# Load API key from .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise EnvironmentError("OPENAI_API_KEY is not set in the .env file.")

class ContextProvider:
    def get_context(self, source_identifier):
        raise NotImplementedError("Must implement get_context()")

class GitHubRepoProvider(ContextProvider):
    def __init__(self):
        self.api_base = "https://api.github.com"
        self.raw_base = "https://raw.githubusercontent.com"
        self.file_extensions = ['.py', '.js', '.ts', '.html', '.css', '.md', '.txt', '.json']

    def get_default_branch(self, owner, repo):
        resp = requests.get(f"{self.api_base}/repos/{owner}/{repo}")
        resp.raise_for_status()
        return resp.json().get("default_branch", "main")

    def get_context(self, repo_url):
        print(f"Fetching GitHub repository: {repo_url}")
        parsed = urlparse(repo_url)
        parts = parsed.path.strip('/').split('/')
        if len(parts) < 2:
            return "Invalid GitHub repository URL"

        owner, repo = parts[0], parts[1]
        try:
            branch = self.get_default_branch(owner, repo)
            tree_url = f"{self.api_base}/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
            response = requests.get(tree_url)
            response.raise_for_status()
            files = [
                item for item in response.json().get('tree', [])
                if item['type'] == 'blob' and any(item['path'].endswith(ext) for ext in self.file_extensions)
            ]

            all_content = []
            for file in files[:20]:  # Limit for safety
                file_url = f"{self.raw_base}/{owner}/{repo}/{branch}/{file['path']}"
                try:
                    content = requests.get(file_url).text
                    all_content.append(f"{file['path']}:\n{content}")
                except Exception as e:
                    print(f"Failed to fetch {file['path']}: {e}")
                time.sleep(0.5)  # Avoid rate limit

            return "\n\n".join(all_content)

        except Exception as e:
            return f"Error: {str(e)}"

class WebsiteProvider(ContextProvider):
    def get_context(self, website_url):
        print(f"Fetching website: {website_url}")
        try:
            response = requests.get(website_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            for tag in soup(["script", "style"]):
                tag.decompose()

            text = '\n'.join(chunk.strip() for chunk in soup.get_text().splitlines() if chunk.strip())
            return text

        except Exception as e:
            return f"Error: {str(e)}"

class ContextRouter:
    def __init__(self):
        self.providers = {
            'github': GitHubRepoProvider(),
            'website': WebsiteProvider()
        }

    def get_provider_type(self, url):
        return 'github' if 'github.com' in url else 'website'

    def get_context(self, url):
        provider_type = self.get_provider_type(url)
        provider = self.providers.get(provider_type)
        return provider.get_context(url) if provider else "No provider for this URL."

class MCPSystem:
    def __init__(self):
        self.router = ContextRouter()
        self.qa_system = None
        self.current_source = None

    def load_source(self, source_url):
        context = self.router.get_context(source_url)

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        texts = splitter.split_text(context)
        embeddings = OpenAIEmbeddings()
        vectorstore = Chroma.from_texts(texts, embeddings, metadatas=[{"source": i} for i in range(len(texts))])

        self.qa_system = RetrievalQA.from_chain_type(
            llm=OpenAI(temperature=0),
            chain_type="stuff",
            retriever=vectorstore.as_retriever(search_kwargs={"k": 5})
        )
        self.current_source = source_url
        return f"✅ Source loaded: {source_url}"

    def process_query(self, query):
        if not self.qa_system:
            return "⚠️ Please load a source first."
        return self.qa_system.run(query)

    def generate_code(self, feature_request):
        if not self.qa_system:
            return "⚠️ Please load a source first."

        prompt = (
            f"Based on the existing code and documentation of the project at {self.current_source}, "
            f"generate code for this feature: {feature_request}\n\n"
            "The code should be compatible, well-commented, and follow the same conventions."
        )

        try:
            response = openai.completions.create(
                model="gpt-4o mini",
                prompt=prompt,
                max_tokens=150,  # You can adjust max_tokens if necessary
                temperature=0.7  # You can adjust temperature for creativity control
            )
            return response['choices'][0]['text'].strip()  # Adjusted for the new response format
        except Exception as e:
            return f"❌ Code generation failed: {str(e)}"

def demonstrate_mcp():
    mcp = MCPSystem()
    source_url = input("🔗 Enter GitHub repo or website URL: ").strip()
    print(mcp.load_source(source_url))

    while True:
        print("\nOptions:\n1. Ask a question\n2. Generate code\n3. Exit")
        choice = input("Select (1-3): ").strip()

        if choice == '1':
            query = input("❓ Enter your question: ")
            print("\n📘 Answer:\n", mcp.process_query(query))
        elif choice == '2':
            feature = input("🛠 Describe the feature you want: ")
            print("\n💡 Suggested Code:\n", mcp.generate_code(feature))
        elif choice == '3':
            print("👋 Goodbye!")
            break
        else:
            print("❗ Invalid option, try again.")

if __name__ == "__main__":
    demonstrate_mcp()
