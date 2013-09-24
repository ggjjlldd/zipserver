zipserver
=========

used to zip file and dir

this used stream to send zip file

you can get zip file size before zip file package

api introduction:

http://server:port/zip_package?filelist=http://filelist address

data structure:
filelist used json format:

{"stat":"200",
"attr":[
"zipname":"xxx.zip",
"zipencoding":"utf-8"}
],
"zipfiles":[
[
{"path":xxx},
{"size",xxx},
{"url",xxx}
],
...
]
]
}

