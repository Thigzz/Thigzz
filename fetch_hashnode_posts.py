import requests
import xml.etree.ElementTree as ET

# URL of the RSS feed for your Hashnode blog
rss_url = "https://ithoughtialready.hashnode.dev/rss.xml"

# Function to fetch and parse RSS feed
def fetch_blog_posts():
    response = requests.get(rss_url)
    response.raise_for_status()
    
    # Parse the XML RSS feed
    root = ET.fromstring(response.content)
    items = root.findall(".//item")[:5]  # Get the first 5 posts

    # Extract title, link, and description for each post
    posts = []
    for item in items:
        title = item.find("title").text
        link = item.find("link").text
        description = item.find("description").text
        posts.append(f"- [{title}]({link}) - {description[:100]}...")  # Limit description to 100 characters

    return posts

# Function to update README.md with the latest blog posts
def update_readme(posts):
    readme_path = "README.md"

    # Read the current content of the README file
    with open(readme_path, "r", encoding="utf-8") as file:
        readme_content = file.readlines()

    # Find the section for Hashnode blog posts and update it
    start_tag = "<!-- HASHNODE-BLOG:START -->"
    end_tag = "<!-- HASHNODE-BLOG:END -->"
    
    start_index = None
    end_index = None
    
    for index, line in enumerate(readme_content):
        if start_tag in line:
            start_index = index
        if end_tag in line:
            end_index = index

    if start_index is not None and end_index is not None:
        # Update the section with new blog posts
        new_content = readme_content[:start_index + 1] + [f"\n## 📝 Latest Blog Posts\n\n"] + posts + readme_content[end_index:]
        with open(readme_path, "w", encoding="utf-8") as file:
            file.writelines(new_content)

# Main function to fetch posts and update README
def main():
    try:
        posts = fetch_blog_posts()
        update_readme(posts)
        print("README.md updated successfully with the latest blog posts!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
