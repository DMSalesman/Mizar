## Purpose

Mizar is a Python (3.5+) tool aimed at assembling MarkDown manuals for Android apps.

Its main goal is to reuse the same string terminology defined in the `strings.xml` files, in order to enforce consistency between the strings visible in the UI of your app and those defined in your guide.

-----

## Usage

Mizar requires two mandatory arguments and supports one optional argument as well. You'll be able to see a short usage message by means of:

    python mizar.py -h

Such an input will yield you:

    usage: mizar.py [-h] xml parts [guide]
    
    Assembles a MarkDown guide from a collection of MD files and one XML file. The guide will be located where the parts reside, or at the chosen location.
    
    positional arguments:
      xml         path to the xml file (single file)
      parts       path to the guide parts (directory)
      guide       name and/or full path of the unified guide to be generated
    
    optional arguments:
      -h, --help  show this help message and exit

While the `xml` and `parts` arguments are self-explanatory, `guide` might be slightly unclear. It is not the path of the unified MarkDown guide, but only its filename. If not specified, it defaults to `manual.md`.

-----

## Accepted file names and format

At the present moment, Mizar does filter out XML files according to the `.xml` extension.

About guide parts, Mizar won't care whether you assign them the `.md` extension or not. It will search for any file in the given folder whose name begins with an arbitrary number of digits followed by an underscore, such as:

    00_prologue.md

It will be your care to name your guide parts appropriately. The files will be scanned in ascending order.

-----

## Output location

**If a path and a filename have been provided:** the guode will be located in the chosen path, under the chosen filename.

**If only a filename has been provided:** the guide will be located in the same folder as the guide parts, under the chosen filename.

**If neither a path nor a filename have been provided:** the guide will be located in the same folder as the guide parts, under the `manual.md` filename.

-----

## Guide parts

When analyzing the guide parts, Mizar will look for custom references defined by you. Such references must resemble the format below:

    {name}

The string `name` in the above example is to be replaced with the value of the `name` attribute pertaining to your XML's `<string>` tag.

This way, if your `strings.xml` defines a string with the following tag:

    <string name="fm">File Manager</string>

you'll be able to get the `File Manager` string in your MarkDown guide by writing:

    {fm}

where you want that string to appear. This syntax is fully compatible with any other MD syntax. For instance, if you wanted the above string to be bold, you used:

    **{fm}**

to get **File Manager** in your unified guide.

-----

## References to other strings

Mizar is able to follow references to other strings in the format:

    @string/stringName

For example, if you had two strings like the following:

    <string name="width">Big</string>
    <string name="height">@string/width</string>

you'll be able to get the string `Big` with:

    {width}

and with:

    {height}

as well.

-----

## Unsuccessful substitutions

If Mizar finds one or more `{keywords}` without matches into the given `strings.xml`, it won't abort abruptly. Instead, it'll report the keywords in question in the shell, and such keywords will be written verbatim in the unified guide.