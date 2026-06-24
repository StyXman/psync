A repository mirroring tool with consistency in mind.

Works like this:

1. downloads new versions of the databases that define the contents of a repo in a temp directory
2. downloads all new packages on the remote that are not already present on the local mirror
3. puts the new databases where they should be
4. deletes files in the repo that are not referenced by the new databases, cleaning up old versions of packages.

If anything goes wrong in step:

1. old dbs and files are in place, the repo is still usable
2. same
3. I don’t remember, it probably needs some work around this
4. the new DBs reference the new files, and the old ones not deleted will be in the next time this runs

It supports several repo formats, including debian, yum, but not sure dnf (in case it has changed in any way).
