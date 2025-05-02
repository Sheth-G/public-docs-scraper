import requests
from agents import Agent, Runner, WebSearchTool
from pydantic import BaseModel, RootModel
from typing import Dict, List


# Define the prompts as variables
primary_agent_prompt = """
You are an expert AI documentation analyst specializing in deconstructing complex product documentation into structured modules and submodules.

Objective:
Analyze the provided documentation to identify all possible modules and their corresponding submodules. Your tasks include:

1. Module Identification:
   - Determine top-level modules based on primary sections or topics within the documentation.
   - Ensure comprehensive coverage, considering all functional areas.

2. Submodule Classification:
   - For each identified module, list all logically connected subtopics as submodules.
   - Group related functionalities under appropriate submodules.

3. Description Generation:
   - Provide detailed and accurate descriptions for each module and submodule.
   - Base descriptions solely on information extracted from the documentation.

Constraints:
- Do not infer or assume information not present in the documentation.
- Maintain objectivity and avoid subjective interpretations.
- Ensure that all modules and submodules are accounted for; aim for exhaustive coverage.

Output Format (JSON):
{
  {
     "module": "Module_1",
     "description": "Detailed description of Module_1.",
     "submodules": {
        "Submodule_1": "Detailed description of Submodule_1.",
        "Submodule_2": "Detailed description of Submodule_2"
        // ... additional submodules
     }
  },
  {
     "module": "Module_2",
     "description": "Detailed description of Module_2.",
     "submodules": {
        "Submodule_1": "Detailed description of Submodule_1.",
        "Submodule_2": "Detailed description of Submodule_2"
        // ... additional submodules
     }
  }
  // ... additional modules
}

Example:
For instance, consider the product "Instagram":
{
  {
     "module": "Account Settings",
     "description": "Includes features and tools for managing Instagram account preferences, privacy, and credentials.",
     "submodules": {
        "Change Username": "Explains how to update your Instagram handle and display name via account settings."
     }
  },
  {
     "module": "Content Sharing",
     "description": "Covers tools and workflows for creating, editing, and publishing content on Instagram.",
     "submodules": {
        "Creating Reels": "Provides instructions for recording, editing, and sharing short-form video content using Reels.",
        "Tagging Users": "Details how to tag individuals or businesses in posts and stories for engagement."
     }
  }
}
Ensure similar structuring and detailing for the provided documentation.
"""

backup_agent_prompt = """
You are a backup web scraping agent tasked with validating and enhancing the modular breakdown of product documentation.

Objective:
Given a URL and an initial JSON structure detailing modules and submodules:

1. Validation:
   - Scrape the provided web page thoroughly.
   - Compare the scraped content against the initial JSON to identify any missing modules or submodules.

2. Enhancement:
   - For any identified omissions, add the missing modules or submodules to the JSON.
   - Ensure that each addition includes a detailed and accurate description based solely on the scraped content.

Constraints:
- Do not remove or alter existing entries in the initial JSON unless corrections are necessary based on the documentation.
- Avoid assumptions; only include information explicitly present in the documentation.
- Maintain the original JSON structure and formatting.

Output Format (JSON):
Return the updated JSON object, preserving the structure:
{
  {
    "module": "Module_1",
    "description": "Detailed description of Module_1.",
    "submodules": {
      "Submodule_1": "Detailed description of Submodule_1.",
      "Submodule_2": "Detailed description of Submodule_2",
      // ... additional submodules
    }
  }
  // ... additional modules
}

Instructions:
- Ensure that the final JSON comprehensively represents all modules and submodules present in the documentation.
- Double-check for any overlooked sections or functionalities.
- Provide clear and concise descriptions for each entry.
"""

# Initialize agents
agent = Agent(
    name="Web Scraping Agent",
    tools=[WebSearchTool()],
    model="gpt-4o",
    instructions=primary_agent_prompt,
)

backup_agent = Agent(
    name="Backup Web Scraping Agent",
    tools=[WebSearchTool()],
    model="gpt-4o",
    instructions=backup_agent_prompt,
)

def is_valid_url(url):
    """Check if the URL is valid and reachable."""
    try:
        session = requests.Session()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0",
            "Referer": url,
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1"
        }
        response = session.get(url, headers=headers, allow_redirects=True, timeout=10)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Invalid or unreachable URL: {url}. Error: {e}")
        return False

def process_urls(urls):
    """Process a list of URLs."""
    for url in urls:
        if not is_valid_url(url):
            continue

        try:
            print(f"Processing URL: {url}")
            result = Runner.run_sync(agent, f"I need the modules and submodules of the following page: {url}.")
            final_result = Runner.run_sync(
                backup_agent,
                f"URL: {url}. Initial JSON : ${result.final_output}"
            )
            print(f"Final output for {url}: {final_result.final_output}")
        except Exception as e:
            print(f"An error occurred while processing {url}: {e}")

if __name__ == "__main__":
    # Take input URLs from the console
    input_urls = input("Enter URLs separated by commas: ").split(",")
    urls = [url.strip() for url in input_urls if url.strip()]
    process_urls(urls)
