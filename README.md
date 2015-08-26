# WebSpider
A python website spider that recursively downloads a webpage.

RUNNING MY PROJECT:

python completion.py ["URL"] - (remove square brackets and quotes)

e.g - 
python completion.py homepages.ecs.vuw.ac.nz/~ian/nwen241/
python completion.py homepages.ecs.vuw.ac.nz/~ian/nwen241
python completion.py http://homepages.ecs.vuw.ac.nz/~ian/nwen241/index.html

The program automatically cleans up the urls so all 3 variations
of the urls above can work. For best results call with the entire url,
as with the other two urls, the recursive version works on the basis 
of the first url, so it may recurse twice due to it not 
recognizing the index.html version

Quick rundown of the code:

Most functions work on the basis of the datapair tuple
which consists of three things, an urlparse, data and a file_extension which
may or may not be used.

The basis of the tuple is the read_url(url) function, this function takes in a url and converts it into a tuple
containing the urlparse object, the data of the url, and the guessed file
extension in the case that "index.html" is not specified in the url. This
works reading the content-type header from the response and using the mimetype
library it guesses the file extension. Due to guess_extensions implementation
the guess_extension returns an extension from a set which varies due to the hash's
so I made it convert to ".html" if it returns ".htm" I linked a post on it
in the comments of the code.

In convert_filename(url, filepath, guessed_file_ext) if the filename
can not be extracted from the url, it is assumed that the url does not contain
a file path so I went on the assumption that it was not specified and gave
it the name "index"

The recursive version works on a set principle, so that the urls already visited get added
to this set when they are read.

Everything else I think is self-explanatory.
