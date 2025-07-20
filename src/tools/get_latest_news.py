from src.tools.base_tool import BaseTool


class GetLatestNewsTool(BaseTool):
    def __init__(
        self,
        name: str = "GetLatestNews",
        description: str = (
            "Search for latest news by query"
        ),
        max_results: int = 10,
    ):
        parameters = [
            {
                "name": "query",
                "type": "str",
                "description": "The search query to find the latest news.",
            }
        ]
        super().__init__(name, description, parameters)
    
    def use_tool(self, query: str) -> str:
        """
        今回はmock toolとしてpre-definedなtextを返す
        """
        return open("resources/latest_news.txt").read()
        