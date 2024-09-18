from flask import Flask, render_template, Response
import json
import sys
import os
import hashlib
from datetime import datetime, timezone
import urllib.parse
import markdown

def sha256_hash(input_string):
    sha256 = hashlib.sha256()
    sha256.update(input_string.encode('utf-8'))
    return sha256.hexdigest()

def generate_rss():
    xml_template = f"""
<rss version="2.0">
    <channel>
        <title>{blog_title}</title>
        <link>{base_url}</link>
        <description>{blog_slogan}</description>
        <language>en-us</language>
        <managingEditor>{webmaster_email} ({webmaster_name})</managingEditor>
        <webMaster>{webmaster_email} ({webmaster_name})</webMaster>
        <generator>nikolan's super silly blog software :3</generator>
    """
    for post in posts_dict: # add xml for each post
        xml_template += '''
        <item>
          <title>{}</title>
          <link>{}</link>
          <pubDate>{}</pubDate>
        </item>
        '''.format(post['title'], post['post_fulllink'],
                   datetime.fromtimestamp(post['timestamp_published'], tz=timezone.utc).strftime("%a, %d %b %Y at %H:%M:%S GMT"))
    xml_template += "</channel></rss>" # finish rss
    return xml_template

def config_gen():
    temp_done = False
    print("-- Config Wizard --")
    while not temp_done:
        temp_title = input("- Blog Title: ")
        temp_slogan = input("- Blog Slogan/Description: ")
        temp_password = sha256_hash(input("- Admin Password: "))
        temp_posts_dir = input("- Posts Directory (posts): ")
        temp_base_url = input("- Base URL (example: http://localhost:5000/): ")
        temp_webmaster_email = input("- Webmaster/editor email")
        temp_webmaster_name = input("- Webmaster/editor name")
        temp_json = {
            "title": temp_title,
            "slogan": temp_slogan,
            "admin": temp_password,
            "posts_dir": temp_posts_dir if not temp_posts_dir == "" else "posts",
            "base_url": temp_base_url,
            "webmaster_email": temp_webmaster_email,
            "webmaster_name": temp_webmaster_name
        }
        temp_choice = input("- Save Config to config.json? (will overwrite) (y/n) ")
        if temp_choice.lower() == "yes" or temp_choice.lower() == "y":
            temp_done = True
            with open("config.json", "w") as temp_file:
                json.dump(temp_json, temp_file, indent=4)
            print("-- Wizard Completed --")
        else:
            print("-- Wizard not Completed --")

def refresh_posts():
    global posts_dict
    posts_dict = []
    newfiles_list = []
    # first, redo the json files
    for post in os.listdir(posts_dir):
        post_path = os.path.join(posts_dir, post)
        if not os.path.isfile(post_path) or not post.lower().endswith('.md'):
            continue
        with open(post_path, 'r', encoding='utf-8') as file:
            # get post title
            first_line = file.readline().strip()
            namep = post[:-3].replace(' ', '-').replace('_', '-')  # normal version of the file name
            if first_line.startswith('# '): # check if post has a valid title
                title = first_line[2:].strip()
                # check if post existed before, if so get original created date, else set to current
                # might as well get the value of "auto" while the file is open ( refer to line 60 )
                auto_value = True
                old_path = os.path.join('system', post[:-3] + '.json')
                if os.path.exists(old_path):
                    with open(old_path, 'r') as old_file:
                        old_json = json.load(old_file)
                        auto_value = old_json.get('auto', True)
                        timestamp_published = old_json.get('timestamp_published')
                        if not timestamp_published:
                            timestamp_published = datetime.now().timestamp()
                else:
                    timestamp_published = datetime.now().timestamp()
                # generate json and save it :3
                urlsafe = urllib.parse.quote(post[:-3].replace(' ', '-').replace('_', '-'))  # url safe version of the file name
                md_path = post_path  # path to the markdown file
                post_fulllink = base_url + "posts/" + urlsafe  # full url for the markdown file
                post_json = {
                    "title": title,
                    "timestamp_published": int(timestamp_published),
                    "auto": True, # this means that the json was auto generated and will be touched next time too. if you want
                                  # to manually override something (such as title), edit the file manually, change the value
                                  # and set this to false
                    "urlsafe": urlsafe,
                    "name": namep,
                    "md_path": md_path,
                    "post_fulllink": post_fulllink
                }
                newfiles_list.append(namep)
                if auto_value is True:
                    # write the new json
                    with open(os.path.join('system', namep + '.json'), 'w') as post_file:
                        json.dump(post_json, post_file, indent=4)
    # second, update the dict
    for json_file in os.listdir('system'):
        json_path = os.path.join('system', json_file)
        if not json_file.lower().endswith('.json'):
            continue
        with open(json_path, 'r', encoding='utf-8') as file:
            posts_dict.append(json.load(file))

    newfiles_with_ext = [f"{file}.json" for file in newfiles_list]

    for filery in os.listdir('system'):
        if filery not in newfiles_with_ext:
            os.remove(os.path.join('system', filery))

def init_directories():
    # check directories
    required_paths = ['templates', 'templates/homepage.html']
    for path in required_paths:
        if not os.path.exists(path):
            print(f"[INIT] {path} not found, exiting")
            sys.exit()
    
    # make required directories
    required_system_paths = ['system']
    for path in required_system_paths:
        if not os.path.exists(path):
            print(f"[INIT] Creating {path}")
            os.makedirs(path)

def read_config():
    global blog_title, blog_slogan, blog_password, posts_dir, base_url, webmaster_email, webmaster_name
    if not os.path.exists("config.json"):
        print("[INIT] Config not found")
        config_gen()
    print("[INIT] Reading config file")
    with open('config.json', 'r') as config_file:
        config_json = json.load(config_file)

        if not config_json.get("title"):
            print("[INIT] Blog title missing, exiting")
            sys.exit()
        else:
            blog_title = config_json.get("title")

        if not config_json.get("admin"):
            print("[INIT] Admin password missing, exiting")
            sys.exit()
        else:
            blog_password = config_json.get("admin")

        if not config_json.get("posts_dir"):
            print("[INIT] Posts directory missing, exiting")
            sys.exit()
        else:
            posts_dir = config_json.get("posts_dir")
            if not os.path.exists(posts_dir):
                if not posts_dir == 'posts':
                    print("[INIT] Posts directory does not exist, exiting")
                    sys.exit()
                else:
                    os.makedirs(posts_dir)

        if not config_json.get("base_url"):
            print("[INIT] Base URL missing, exiting")
            sys.exit()
        else:
            base_url = config_json.get("base_url")

        if not config_json.get("slogan"):
            print("[INIT] Slogan missing, exiting")
            sys.exit()
        else:
            blog_slogan = config_json.get("slogan")

        if not config_json.get("webmaster_email"):
            print("[INIT] Webmaster Email missing, defaulting to anonymous@example.com")
            webmaster_email = "anonymous@example.com"
        else:
            webmaster_email = config_json.get("webmaster_email")

        if not config_json.get("webmaster_name"):
            print("[INIT] Webmaster Name missing, defaulting to Anonymous")
            webmaster_name = "Anonymous"
        else:
            webmaster_name = config_json.get("webmaster_name")

app = Flask(__name__)

@app.route('/')
def homepage():
    return render_template('homepage.html', title=blog_title, slogan=blog_slogan, posts=posts_dict)

@app.route('/posts/<postname>')
def post_read(postname):
    post_filedir = os.path.join('system', str(urllib.parse.unquote(postname)) + ".json")
    if not os.path.exists(post_filedir): # if it doesn't exist
        return "Post not found", 404
    else: # if it does exist
        with open(post_filedir, 'r', encoding='utf-8') as fileready: # read metadata
            file_json = json.load(fileready)
        if not os.path.exists(file_json['md_path']):
            return "Post metadata found, but no post content", 404
        with open(file_json['md_path'], 'r', encoding='utf-8') as fileready2: # read content
            post_content = fileready2.read()
        post_title = file_json.get("title", "No Title")
        post_created = file_json.get("timestamp_published", "0")
        post_content = markdown.markdown(post_content.strip(f"# {post_title}"))
        post_url = f"{base_url}posts/{postname}"
        return render_template('reader.html', title=post_title, content=post_content, timestamp_published=post_created, posturl=post_url)
    
@app.route('/feed')
def rss_feed_end():
    rss_content = generate_rss()
    return Response(rss_content, mimetype='text/xml') 

if __name__ == '__main__':
    init_directories()
    read_config()
    refresh_posts()
    print("[INIT] Starting")
    app.run(debug=True)