import feedparser
import os # For checking if running in GitHub Actions

FEED_URL = "https://ithoughtialready.hashnode.dev/rss.xml"
NUM_POSTS = 1 # Number of posts to fetch (you can change this, e.g., to 5)

# --- IMPORTANT: These are your specific markers from your README.md ---
marker_start = ""
marker_end = ""
readme_path = "README.md" # Assumes README.md is in the root of your repository

print(f"Attempting to parse feed from: {FEED_URL}")
feed = feedparser.parse(FEED_URL)

# --- Enhanced Error Checking ---
is_github_actions = os.getenv("GITHUB_ACTIONS") == "true"
bozo = 0 # Default to 0 (false)
bozo_exception_message = "No exception"

if hasattr(feed, 'bozo') and feed.bozo: # Check if 'bozo' attribute exists and is true
    bozo = feed.bozo
    if hasattr(feed, 'bozo_exception'):
        bozo_exception_message = str(feed.bozo_exception)
    print(f"WARNING: Feed is 'bozo' (potentially malformed or an error occurred). Bozo status: {bozo}")
    print(f"Bozo Exception: {bozo_exception_message}")

http_status = "Not available" # Default status
if hasattr(feed, 'status'):
    http_status = feed.status
    print(f"HTTP Status from feed request: {http_status}")
    if http_status == 429:
        print("CRITICAL ERROR: Received HTTP 429 Too Many Requests. Hashnode is rate-limiting this request.")
        if is_github_actions:
            print("Exiting gracefully due to 429 error in GitHub Actions. README will not be updated.")
            exit(0) # Exit gracefully, job will succeed, no commit will happen.

if not feed.entries:
    print("No blog posts found in feed.entries.")
    if hasattr(feed, 'status') and feed.status == 429:
        # This case should have been caught above if running in GitHub Actions and exited.
        # If not in GH Actions, or if logic changes, this ensures it's handled.
        print("This was due to a 429 error. Exiting gracefully as handled above.")
        exit(0)
    else:
        # If not a 429, and entries are empty, it's a different issue or an empty feed.
        print("Exiting with error code 1 as feed.entries is empty and not due to a handled 429.")
        exit(1) # Exit with error, job will fail.
# --- End of Enhanced Error Checking ---

# If feed.entries is still empty here (e.g., if feed was bozo but not 429, and entries empty)
# This check ensures we don't proceed if, for any reason not caught above, entries are missing.
if not feed.entries:
    print("Final check: No entries to process for README update. Exiting gracefully.")
    exit(0)

latest_posts = feed.entries[:NUM_POSTS]
post_lines = []

for post in latest_posts:
    title = post.title
    url = post.link
    post_lines.append(f"- [{title}]({url})") # Simple list format

new_blog_content_for_readme = f"{marker_start}\n" + "\n".join(post_lines) + f"\n{marker_end}"

# Read existing README
try:
    with open(readme_path, "r", encoding="utf-8") as f:
        readme_content = f.read()
except FileNotFoundError:
    print(f"Error: {readme_path} not found.")
    exit(1)

# Check if the content to be inserted is identical to what's already there
# to avoid unnecessary commits.
current_blog_section_start_idx = readme_content.find(marker_start)
current_blog_section_end_idx = readme_content.find(marker_end)

# Check if markers are found and if end_marker is after start_marker
if current_blog_section_start_idx != -1 and \
   current_blog_section_end_idx != -1 and \
   current_blog_section_end_idx > current_blog_section_start_idx:
    
    # Extract the part of the string that includes the end marker itself
    # for accurate comparison and replacement.
    # The content *between* the markers starts after marker_start.
    # The full block to replace includes marker_start and ends with marker_end.
    
    existing_full_block = readme_content[current_blog_section_start_idx : current_blog_section_end_idx + len(marker_end)]

    if existing_full_block == new_blog_content_for_readme:
        print("No change in blog post content. Nothing to update.")
        exit(0) # Exit gracefully
else:
    print(f"Blog markers ('{marker_start}', '{marker_end}') not found, in wrong order, or incomplete in README.md.")
    print("Please ensure both markers exist and START is before END.")
    # If markers aren't found, we might not want to fail the build,
    # or we might. For now, exiting with error.
    exit(1)


# Replace the blog section
# The new content already includes the markers.
updated_readme = readme_content[:current_blog_section_start_idx] + \
                 new_blog_content_for_readme + \
                 readme_content[current_blog_section_end_idx + len(marker_end):]


# Write updated README
with open(readme_path, "w", encoding="utf-8") as f:
    f.write(updated_readme)

print(f"README updated successfully with {len(latest_posts)} post(s).")
