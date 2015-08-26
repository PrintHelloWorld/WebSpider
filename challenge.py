from urllib.parse import urlparse
from urllib.request import pathname2url, url2pathname
from os.path import basename, dirname, splitext
from mimetypes import guess_extension
import os
import urllib.request
import sys
import re

visited_links  = set()

def main(url):
	# cleans url for consistency in the program
	url = clean_url(url)
	# authorize url as being valid
	if authorize_url(url):
		# construct a datapair tuple for first url
		datapair = read_url(url)
		if datapair:
			# return a list of all datapairs
			hyperlink_datapair_list = recurse_find_hyperlinks([], datapair)
			for datapair_recurse in hyperlink_datapair_list:
				download_html(datapair_recurse)
				download_images(datapair_recurse)
		else:
			print("Network Error")
	else:
		print("argument is not a valid url")

"""
Reads a url to return a tuple of urlparse, data, file extenstion
"""
def read_url(url):
	try:
		# divide url into properties
		parts = urlparse(url)
		# retrieve response of url
		response = urllib.request.urlopen(url)
		# read the response html page source
		data = response.read()
		# retrieve content type
		content_type = response.headers['content-type']
		guessed_file_ext = guess_extension(content_type.split()[0].rstrip(";"))
		# Fixes in oddity in guess_extension, due to http://www.gossamer-threads.com/lists/python/python/1118334
		if guessed_file_ext == ".htm":
			guessed_file_ext = ".html"
		# add to visited set of links
		visited_links.add(url)
		# combine into a tuple of a urlparse and the data associated with that url
		return (parts, data, guessed_file_ext)
	except Exception as e:
		print(str(e))

"""
Returns a list of tuples of urlparse to data
"""
def recurse_find_hyperlinks(hyperlink_datapair_list, datapair):
	hyperlink_datapair_list.append(datapair)
	for hyperlink in find_hyperlinks(datapair):
		datapair_new = read_url(clean_url(hyperlink))
		# dont follow broken links
		if datapair_new:
			recurse_find_hyperlinks(hyperlink_datapair_list, datapair_new)
		else:
			return hyperlink_datapair_list
	return hyperlink_datapair_list

"""
Returns all hyperlinks in page, removing
any hyperlinks that redirect to a different website
"""
def find_hyperlinks(datapair):
	#hyperlink regex
	hyperlinkregex = 'a .*?href="(.*?)"'
	#list of all hyperlinks
	hyperlinks = re.findall(hyperlinkregex, str(datapair[1]))
	for i, hyperlink in enumerate(hyperlinks):
		# edits any links that are relative into absolute urls
		if not is_absolute(hyperlink):
			if hyperlink.startswith("/"):
				hyperlinks[i] = dirname(datapair[0].geturl()) + hyperlink
			else:
				hyperlinks[i] = dirname(datapair[0].geturl()) + "/" + hyperlink
	# removes all hyperlinks thats netloc is different from the base urls, and that have been already visited
	hyperlinks[:] = [hyperlink for hyperlink in hyperlinks if checknetloc(hyperlink,datapair) and hyperlink not in visited_links]
	return hyperlinks

"""
Creates recursive directory structure from url and returns fullname to it
"""
def create_directory(url):
	# gets current directory
	cwd = os.getcwd()
	fullname = os.path.join(cwd, dirname(url))
	if not os.path.exists(fullname):
		os.makedirs(fullname)
	return fullname

"""
Saves the html source in the datapair to the specified directory
"""
def download_html(datapair):
	# data pair = [0] - urlparse [1] - data/html source  [2] - file extension
	try:
		# returns the filename to save the html link as
		fullname = create_directory(datapair[0].netloc + datapair[0].path)
		filename = convert_filename(datapair[0].geturl(), fullname, datapair[2])
		saveFile = open(os.path.join(fullname, filename), "w")
		saveFile.write(str(datapair[1]))
		saveFile.close
	except Exception as e:
		print(str(e))

"""
Finds all images in the html source and saves them as images
to the specified directory
"""
def download_images(datapair):
	# data pair [0] - urlparse [1] - data
	# regex to find  image tags
	regex = 'img .*?src="(.*?)"'
	# save a list of all the urls to images
	imgurls = re.findall(regex, str(datapair[1]))
	# for reach img url
	for imgurl in imgurls:
		if not is_absolute(imgurl):
				imgurl_fullpath	= dirname(datapair[0].geturl()) + "/" + imgurl
		else:
			imgurl_fullpath = imgurl
		try:
			imgData = urllib.request.urlopen(imgurl_fullpath)
			fullname = create_directory(imgurl_fullpath[7:]) #removes the http:// from full path
			imagename = convert_filename(imgurl_fullpath, fullname, datapair[2])
			saveImage = open(os.path.join(fullname, imagename), 'wb')
			saveImage.write(imgData.read())
			saveImage.close()
		except Exception as e:
			print(str(e))

"""
Converts the parsed in filename to a new filename if original filename exists
in the current directory
"""
def convert_filename(url, filepath, guessed_file_ext):
	filename, file_ext = splitext(basename(url))
	# handles the case where the url specifies a directory path other than a file path
	if not filename:
		filename = "index"
	if not file_ext:
		actual_file_ext = guessed_file_ext
	else:
		actual_file_ext = file_ext
	fullname = filename + actual_file_ext
	for i in range(1,10):
		if os.path.exists(os.path.join(filepath, fullname)):
			fullname = filename + str(i) + actual_file_ext
	return fullname

"""
Appends http protocool scheme to url if needed
"""
def clean_url(url):
	# clean url to include http:// naming convention
	if not url.startswith("http://"):
		url = "http://" + url
	if basename(url) and not "." in basename(url):
		url = url + "/"
	return url

"""
Checks url is valid
"""
def authorize_url(url):
	# divide url into properties
	parts = urlparse(url)  
	if not parts.scheme or not parts.netloc:  
		return False
	return True

"""
Returns true if a url is absolute or false if its relative 
"""
def is_absolute(url):
	# returns true if the url is absolute
	return bool(urlparse(url).netloc)

"""
Returns True if hyperlinks netloc is equal to current page
"""
def checknetloc(hyperlink, datapair):
	parts = urlparse(hyperlink)
	if parts.netloc == datapair[0].netloc:
		return True
	return False

if __name__ == "__main__":
	main(sys.argv[1])