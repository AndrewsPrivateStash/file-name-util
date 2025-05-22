<pre>
Renaming util, that can recursively rename files, directories, or both;
mapping the names to various format type {snake, camel, space}.

When the -f flag is not set, it will parse the name automatically splitting on spaces, _,
and common seperator chars: {. , / + -} then treat each element in the resultant list
as camel case (effectively it looks for all formats)

The -l flag only prints what the util would rename files to, but doesn't modify anything,
which is useful for testing the command before commiting the changes.

Generally I'd suggest throwing a shebang at the top `#! /usr/bin/env python3`
and droping the script in a personal bin dir in your PATH, (chmod 751) to allow for easy calling.

Typical flow:
    $tree [dir]                         -- what is there
    $rename_files -l [other args] [dir] -- see what it will do
    $rename_files [other args] [dir]    -- then do it

</pre>


```
usage: rename_files.py [-h] [-f {cam,snake,space,auto}] [-t {cam,snake,space}] [-r] [-p] [-d] [-x] [-l] [-e EXT]
                       [-j JANKREMOVE] [-s SWAP] [--OneDir]
                       Path

positional arguments:
  Path                  path containing the files to convert

options:
  -h, --help            show this help message and exit
  -f {cam,snake,space,auto}, --From {cam,snake,space,auto}
                        from type; default = auto
  -t {cam,snake,space}, --To {cam,snake,space}
                        to type; default = snake
  -r, --Recursive       recursive process
  -p, --PreserveCase    preserve the case in names found
  -d, --IncludeDirs     process directory names as well
  -x, --SkipFiles       suppress file modification
  -l, --ListOps         list file modifications only, no mutations
  -e EXT, --Ext EXT     specifies the extenions to modify, otherwise all
  -j JANKREMOVE, --JankRemove JANKREMOVE
                        string with jank chars to remove from file name
  -s SWAP, --Swap SWAP  swap chars to replace with _
  --OneDir              specifies the path is a single dir
```

<pre>
examples:
$ python rename_files -lrp -e docx -t cam [dir]
list what would be renamed for all files in the dir tree where files have extension .docx and convert to camel case. Preserve the case of chars
</pre>