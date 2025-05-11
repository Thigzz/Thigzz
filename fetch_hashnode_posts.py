import requests

USERNAME = "ithoughtialready"  # Replace with your Hashnode username
README_FILE = "README.md"
START_COMMENT = "<!-- HASHNODE-BLOG:START -->"
END_COMMENT = "<!-- HASHNODE-BLOG:END -->"

query = """
{
  user(username: "%s") {
    publication {
      posts(page: 0) {
        title
        brief
        slug
        dateAdded
      }
    }
  }
}
""" % USERNAME

response = requests.post(
    "https://api.hashnode.com/",
    json={"query": query}
)

if response.status_code == 200:
    data = response.json()
    posts = data["data"]["user"]["publication"]["posts"][:5]
    lines = [START_COMMENT]
    for post in posts:
        title = post["title"]
        url = f"https://{USERNAME}.hashnode.dev/{post['slug']}"
        lines.append(f"- [{title}]({url})")
    lines.append(END_COMMENT)

    with open(README_FILE, "r") as file:
        content = file.read()

    start = content.find(START_COMMENT)
    end = content.find(END_COMMENT, start) + len(END_COMMENT)
    new_content = content[:start] + "\n".join(lines) + content[end:]

    with open(README_FILE, "w") as file:
        file.write(new_content)
else:
    print(f"Failed to fetch posts: {response.status_code}")
