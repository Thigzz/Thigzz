import feedparser

FEED_URL = "https://ithoughtialready.hashnode.dev/rss.xml"
NUM_POSTS = 1

readme_path = "README.md"
marker_start = "<!-- BLOG-POST-LIST:START -->"
marker_end = "<!-- BLOG-POST-LIST:END -->"

feed = feedparser.parse(FEED_URL)

if not feed.entries:
    print("No blog posts found.")
    exit(1)

latest_posts = feed.entries[:NUM_POSTS]
post_lines = []

for post in latest_posts:
    title = post.title
    url = post.link
    post_lines.append(f"- [{title}]({url})")

new_content = f"{marker_start}\n" + "\n".join(post_lines) + f"\n{marker_end}"

# Read existing README
with open(readme_path, "r", encoding="utf-8") as f:
    readme_content = f.read()

# Replace the blog section
start = readme_content.find(marker_start)
end = readme_content.find(marker_end) + len(marker_end)
if start != -1 and end != -1:
    updated_readme = readme_content[:start] + new_content + readme_content[end:]
else:
    print("Blog markers not found in README.md.")
    exit(1)

# Write updated README
with open(readme_path, "w", encoding="utf-8") as f:
    f.write(updated_readme)

print("README updated successfully.")
