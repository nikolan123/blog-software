# Niko's Blog Software

## Setup
This software is designed with simplicity in mind. Clone the repository, and run `main.py` (make sure you have all the requirements installed `flask, waitress, markdown`) to launch the initial setup wizard. The wizard will guide you through the generation of the configuration file. Once the configuration is complete, the server will start automatically. You can modify the configuration at any time, and a server restart will apply the changes.

## Adding Posts
To add a new post, drag a markdown (.md) file into the posts directory specified in the config file (`posts_dir`). The new post will appear automatically within 30 seconds (the default refresh interval). For the post to display, it must start with a `#` followed by a title. This will serve as the blog post’s default title, and the default URL will be `/posts/(filename with spaces replaced by hyphens)`. You can customize the URL and title in the 'system' directory. Refer to the Editing Post Title, Publish Dates, and URL section for more details. If you do not have a post to test this with, you can put this file (`README.md`) in your posts directory.

## RSS Feed
An RSS feed is automatically available at `/feed`. No additional setup is required.

## Editing Post Title, Publish Dates, and URL
Each blog post has an associated file in the 'system' directory that stores metadata such as the title, creation timestamp, and URL. These details can be modified easily. If you make any changes, ensure that the `"auto"` field is set to `false` to prevent the system from overwriting your custom metadata during the next refresh.

## Custom Themes
The `stylesheet` option in the configuration file. Defaults to new.css

---

⭐ If you enjoy using this software, please give it a star!<br>
💗 Special thanks to everyone who helped in any way—you're truly amazing!
