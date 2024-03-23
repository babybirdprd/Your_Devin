import json
import requests
from swarms import Agent, Mistral, AbstractLLM
import os
from dotenv import load_dotenv

# Load the environment variables
load_dotenv()


def get_github_repo_page(owner: str, repo: str) -> str:
    """
    Retrieves the HTML content of a GitHub repository page.

    Args:
        owner (str): The owner of the GitHub repository.
        repo (str): The name of the GitHub repository.

    Returns:
        str: The HTML content of the GitHub repository page.

    Raises:
        requests.exceptions.RequestException: If an error occurs while making the request.

    """
    try:
        url = f"https://github.com/{owner}/{repo}"
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for non-200 status codes
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None


def generate_samples(code: str, agent):
    out = agent.run(code)
    return out


# Create a dataset from the github code -- to
def create_dataset_from_repo(
    model: AbstractLLM,
    file_name: str = "dataset.json",
):
    """
    Create a dataset from a GitHub repository.

    Args:
        model (AbstractLLM): The language model to use for generating the dataset.
        file_name (str): The name of the output JSON file.

    """
    # Get the GitHub repository page
    owner = os.getenv("GITHUB_OWNER")
    repo = os.getenv("GITHUB_REPO")

    # Agent
    agent = Agent(
        llm=Mistral(),
        agent_name="Devin",
        max_loops=4,
    )

    # Extract the code from the GitHub repository page
    code = get_github_repo_page(owner=owner, repo=repo)

    # Generate the dataset
    dataset = []
    for example in code:
        # Generate response from the agent
        response = agent(example)

        # Append example and response to the dataset
        dataset.append({"from": code, "value": response})

    # Save the dataset to a file
    dataset_path = os.getenv("DATASET_PATH")
    with open(dataset_path, "w") as file:
        json.dump(dataset, file)

    print(f"Dataset saved to: {dataset_path}")
