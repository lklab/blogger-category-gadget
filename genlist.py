import requests
import json
import urllib.parse

### settings ###
blogId = "4213915415549125978"
key = "AIzaSyDrrFE6eQbzbQ3O9H14W4Zr2Db1F8pogGE"
categories = \
[
	{
		"label" : "unity",
		"name" : "Unity",
		"sub" :
		[
			{"label" : "shader", "name" : "Shaders"},
			{"label" : "plugin", "name" : "Plugin"},
			{"label" : "vr",     "name" : "VR"}
		]
	},
	{
		"label" : "mdd",
		"name" : "MDD",
		"sub" : []
	},
	{
		"label" : "industrial_network",
		"name" : "Industrial networks",
		"sub" : []
	},
	{
		"label" : "etc",
		"name" : "etc.",
		"sub" :
		[
			{"label" : "jni",              "name" : "JNI"},
			{"label" : "machine_learning", "name" : "Machine learning"},
			{"label" : "build_system",     "name" : "Build systems"},
			{"label" : "etc",              "name" : "etc."},
		]
	},
]


### templates ###
templateFile = open("template.html", "r")
template = templateFile.read()
templateFile.close()

categoryTemplate = """
<li>
	<li><span class="caret" id="%(id)s"><a href="/search/label/%(id)s">%(name)s</a></span>
	<ul class="nested">
%(contents)s
	</ul>
</li>
"""

postTemplate = """
<li><mk/>
	<a href="%(url)s">%(title)s</a>
</mk></li>
"""

content = {"posts" : "", "urlToLabels" : ""}


### get posts ###
data = requests.get("https://www.googleapis.com/blogger/v3/blogs/{}/posts?key={}".format(blogId, key))
data = json.loads(data.text)
pageToken = data.get("nextPageToken")

posts = []
posts.extend(data["items"])

while pageToken is not None :
	data = requests.get("https://www.googleapis.com/blogger/v3/blogs/{}/posts?key={}&pageToken={}".format(blogId, key, pageToken))
	data = json.loads(data.text)
	pageToken = data.get("nextPageToken")
	posts.extend(data["items"])


### pocess posts ###
def getPostsFromLabel(posts, label) :
	output = []
	label = "l-" + label

	for post in posts :
		labels = post["labels"]
		for l in labels :
			if l.lower() == label :
				output.append(post)
				break

	return output

for cate1 in categories :
	id1 = "l-" + cate1["label"]
	cate1Content = {"id" : id1, "name" : cate1["name"], "contents" : ""}

	if len(cate1["sub"]) == 0 :
		cate1Posts = getPostsFromLabel(posts, cate1["label"])
		for post in cate1Posts :
			postContent = {"url" : post["url"], "title" : post["title"]}
			cate1Content["contents"] += postTemplate % postContent
			content["urlToLabels"] += "\"{}\" : [ \"{}\" ],\n".format(urllib.parse.urlparse(post["url"]).path, id1)
		content["urlToLabels"] += "\"/search/label/{}\" : [ \"{}\" ],\n".format(id1, id1)

	else :
		for cate2 in cate1["sub"] :
			id2 = "l-" + cate1["label"] + "-" + cate2["label"]
			cate2Content = {"id" : id2, "name" : cate2["name"], "contents" : ""}
			cate2Posts = getPostsFromLabel(posts, cate1["label"] + "-" + cate2["label"])
			for post in cate2Posts :
				postContent = {"url" : post["url"], "title" : post["title"]}
				cate2Content["contents"] += postTemplate % postContent
				content["urlToLabels"] += "\"{}\" : [ \"{}\", \"{}\" ],\n".format(urllib.parse.urlparse(post["url"]).path, id1, id2)
			cate1Content["contents"] += categoryTemplate % cate2Content
			content["urlToLabels"] += "\"/search/label/{}\" : [ \"{}\", \"{}\" ],\n".format(id2, id1, id2)
		content["urlToLabels"] += "\"/search/label/{}\" : [ \"{}\" ],\n".format(id1, id1)

	content["posts"] += categoryTemplate % cate1Content


### output file ###
outputFile = open("output.html", "w")
outputFile.write(template % content)
outputFile.close()
