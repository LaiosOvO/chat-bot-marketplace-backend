import re
from typing import List, Optional
from github import Github, Auth
from github.ContentFile import ContentFile
from langchain.tools import tool
import json

DEFAULT_REPO_NAME = "ant-design/ant-design"

def replace_special_chars(text):
    pattern = r"[><=-]"
    return re.sub(pattern, ' ', text)

def factory(token: Optional[Auth.Token]):
    @tool
    def search_code(
        keyword: str,
        repo_name: Optional[str] = DEFAULT_REPO_NAME,
        max_num: Optional[int] = 5,
    ) -> List[ContentFile]:
        """
        Searches for code files on GitHub that contain the given keyword.

        :param keyword: The search keyword (required).
        :param repo_name: The full name of the repository to search in (optional, format "owner/repo").
        :param access_token: GitHub Access Token for authentication and API rate limit (optional).
        :param max_num: The maximum number of results to return (optional, default is 5).
        :return: A list of ContentFile objects representing the matching code files.
        """
        if token is None:
            g = Github()
        else:
            g = Github(auth=token)
        try:
            query = f"repo:{repo_name} {replace_special_chars(keyword)}"
            # Perform the search for code files containing the keyword
            code_files = g.search_code(query=query)
            if code_files.totalCount:
                code_list = [
                    {
                        "content": file.content,
                        "html_url": file.html_url,
                        "text_matches": file.text_matches,
                    }
                    for file in code_files
                ]
                return json.dumps(code_list[:max_num])
            return json.dumps([])
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    return {
        "search_code": search_code
    }