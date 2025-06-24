import requests
from django.conf import settings

BASE_URL = settings.FACEBOOK_BASE_URL

class FacebookAPIPosts:

    def __init__(self,
                 facebook_page_name: str = None,
                 facebook_access_token: str = None,
                 facebook_page_id: str = None):

        self.facebook_page_name = facebook_page_name
        self.facebook_access_token = facebook_access_token
        self.facebook_page_id = facebook_page_id


    def get_page_posts(self) -> list:
        """
        Retrieves recent posts from a Facebook page using the Graph API.

        Returns:
            list: List of posts or None if an error occurred.
        """
        url = f'{BASE_URL}/{self.facebook_page_id}/feed'

        params = {
            "access_token": self.facebook_access_token,
            "fields": "id,created_time,message"  # Fields to retrieve
        }

        try:
            response = requests.get(url, params=params)
            data = response.json()

            if "error" in data:
                print("Error in request:", data["error"]["message"])
                return None

            posts = data.get("data", [])

            return posts  # Returns list of posts

        except Exception as e:
            print("An error occurred during the request:", str(e))
            return None


    def get_post_comments(self, post_id, filter_type="toplevel", order="reverse_chronological",
                          limit=10):
        """
        Fetches comments from a specific Facebook page post using the Graph API.

        Args:
            post_id (str): The ID of the Facebook post.
            filter_type (str): Filter type for comments (stream or toplevel).
            order (str): Order of comments (chronological or reverse_chronological).
            limit (int): Number of comments to retrieve per request.

        Returns:
            list: List of comments or None if an error occurred.
        """
        url = f"{BASE_URL}/{post_id}/comments"

        params = {
            "access_token": self.facebook_access_token,
            "filter": filter_type,
            "order": order,
            "limit": limit,
            "fields": "id,from,message,created_time"
        }

        try:
            response = requests.get(url, params=params)
            data = response.json()

            if "error" in data:
                print(f"Error in request: {data['error']['message']}")
                return None

            comments = data.get("data", [])
            summary = data.get("summary", {})

            print(f"Total comments: {summary.get('total_count', 0)}")

            for comment in comments:
                user = comment["from"]["name"] if "from" in comment else "Unknown user"
                message = comment.get("message", "No message")
                created_time = comment.get("created_time", "Unknown time")
                print(f"User: {user} | Time: {created_time} | Message: {message}")

            return comments  # Returns list of comment objects

        except Exception as e:
            print(f"An error occurred during the request: {str(e)}")
            return None


    def get_post_reactions(self, post_id, reaction_type=None, limit=10):
        """
        Fetches reactions from a specific Facebook post using the Graph API.

        Args:
            post_id (str): The ID of the Facebook post.
            reaction_type (str): Filter by a specific reaction type (e.g., LIKE, LOVE, WOW, etc.).
            limit (int): Number of reactions to retrieve per request.

        Returns:
            dict: A dictionary containing list of reactions, summary info or None if an error occurred.
        """
        url = f"{BASE_URL}/{post_id}/reactions"

        params = {
            "access_token": self.facebook_access_token,
            "limit": limit,
            "fields": "id,name,type"
        }

        if reaction_type:
            params["type"] = reaction_type.upper()

        try:
            response = requests.get(url, params=params)
            data = response.json()

            if "error" in data:
                print(f"Error in request: {data['error']['message']}")
                return None

            reactions = data.get("data", [])
            summary = data.get("summary", {})

            total_count = summary.get("total_count", 0)
            viewer_reaction = summary.get("viewer_reaction", "NONE")

            print(f"Total reactions: {total_count}")
            print(f"Your reaction: {viewer_reaction}")

            for reaction in reactions:
                user_name = reaction.get("name", "Unknown user")
                reaction_type = reaction.get("type", "NONE")
                print(f"User: {user_name} | Reaction: {reaction_type}")

            return {
                "reactions": reactions,
                "summary": summary
            }

        except Exception as e:
            print(f"An error occurred during the request: {str(e)}")
            return None