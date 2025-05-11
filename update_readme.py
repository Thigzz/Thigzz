import feedparser
import os # For checking if running in GitHub Actions

FEED_URL = "https://ithoughtialready.hashnode.dev/rss.xml"
NUM_POSTS = 1 # You're fetching 1 post, which is good for testing

readme_path = "README.md"
marker_start = ""
marker_end = ""

print(f"Attempting to parse feed from: {FEED_URL}")
feed = feedparser.parse(FEED_URL)

# --- Enhanced Error Checking ---
is_github_actions = os.getenv("GITHUB_ACTIONS") == "true"
bozo = 0
bozo_exception_message = "No exception"

if hasattr(feed, 'bozo') and feed.bozo:
    bozo = feed.bozo
    if hasattr(feed, 'bozo_exception'):
        bozo_exception_message = str(feed.bozo_exception) # Convert exception to string
    print(f"WARNING: Feed is 'bozo' (potentially malformed or an error occurred). Bozo status: {bozo}")
    print(f"Bozo Exception: {bozo_exception_message}")

http_status = "Not available"
if hasattr(feed, 'status'):
    http_status = feed.status
    print(f"HTTP Status from feed request: {http_status}")
    if http_status == 429:
        print("CRITICAL ERROR: Received HTTP 429 Too Many Requests. Hashnode is rate-limiting this request.")
        if is_github_actions:
             # In GitHub Actions, we might want to fail gracefully or not update
             print("Exiting due to 429 error in GitHub Actions to avoid further issues.")
             exit(0) # Exit gracefully without updating to prevent commit of "No posts"
                     # Or exit(1) if you prefer the job to show as failed.
                     # Exiting 0 will make the job succeed but the README won't change.
        # else: # If running locally, you might want to raise an error
        #     raise Exception("HTTP 429 Error from Hashnode")

if not feed.entries:
    print("No blog posts found in feed.entries.")
    # If we exited due to 429 above, this might not be reached in CI
    # If not a 429, or if we decided to continue, this indicates an empty feed.entries
    if http_status != 429: # Only fail hard if it wasn't a 429 we are handling gracefully
        print("Exiting with error code 1 as feed.entries is empty and not due to a handled 429.")
        exit(1)
    else:
        # If it was 429 and we decided to exit(0) earlier, this part is less critical.
        # If script continues, it will try to write an empty list.
        print("Proceeding, but no posts will be updated due to earlier 429 or empty feed.")
        # To prevent writing an empty list if markers exist:
        # exit(0)
# --- End of Enhanced Error Checking ---

# If feed.entries is still empty here (e.g., after a 429 where we didn't exit(1)),
# we should prevent writing an empty list.
if not feed.entries:
    print("Final check: No entries to process for README update. Exiting gracefully.")
    # The commit step in the workflow handles "No changes to commit"
    exit(0)


latest_posts = feed.entries[:NUM_POSTS]
post_lines = []

for post in latest_posts:
    title = post.title
    url = post.link
    post_lines.append(f"- [{title}]({url})")

new_content = f"{marker_start}\n" + "\n".join(post_lines) + f"\n{marker_end}"

# Read existing README
try:
    with open(readme_path, "r", encoding="utf-8") as f:
        readme_content = f.read()
except FileNotFoundError:
    print(f"Error: {readme_path} not found.")
    exit(1)

# Check if the content to be inserted is identical to what's already there
# (between the markers) to avoid unnecessary commits.
current_blog_section_start = readme_content.find(marker_start)
current_blog_section_end = readme_content.find(marker_end) + len(marker_end)
if current_blog_section_start != -1 and current_blog_section_end > current_blog_section_start:
    existing_blog_content = readme_content[current_blog_section_start:current_blog_section_end]
    if existing_blog_content == new_content:
        print("No change in blog post content. Nothing to update.")
        exit(0) # Exit gracefully, "No changes to commit" will be handled by the commit step

# Replace the blog section
start_idx = readme_content.find(marker_start) # Use a different variable name
end_idx = readme_content.find(marker_end) + len(marker_end) # Use a different variable name

if start_idx != -1 and end_idx > start_idx: # Make sure end_idx is after start_idx
    updated_readme = readme_content[:start_idx] + new_content + readme_content[end_idx:]
else:
    print("Blog markers not found or in wrong order in README.md.")
    exit(1)

# Write updated README
with open(readme_path, "w", encoding="utf-8") as f:
    f.write(updated_readme)

print("README updated successfully.")
