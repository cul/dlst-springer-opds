# what we'll need to generate for OPDS but is the same for everything

* type
* a subject of nonfiction



# metadata from springer not sure how to use

* genre (e.g., undergraduate textbook) (data quality is bad?)
* copyright
* ISBN (all 3 kinds)


# Tables

## Title/Edition/Book/Work

* title
* identifier
* language (this is available in springer api)
* description (this is "abstract" in springer api)
* publisher (will need to get this from kbart)
* publication date
* subjects
* series or collection NOTE: this is not in API, but we could get with some work from KBART file. do we want this?




## Contributor

How to handle roles in model??? author, translator, editor, artist, illustrator, letterer, penciler, colorist, inker and narrator.

Spring appears to only have "creator" and "bookEditor" -- which can probably be reliably mapped to author and editor

Springer only includes name, nothing that maps to translated names or sortAs

Do we want a sortAs?? check with existing data model


