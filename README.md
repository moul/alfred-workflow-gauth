Alfred Workflow: Google Authenticator
=====================================

Google Authenticator Workflow for Alfred2

Installation
------------

Create a `~/.gauth` file with your secrets, ie:

```
[google - bob@gmail.com]
secret = xxxxxxxxxxxxxxxxxx

[evernote - robert]
secret = yyyyyyyyyyyyyyyyyy
```

[Download](https://github.com/moul/alfred-workflow-gauth/raw/master/Google%20Authenticator.alfredworkflow) and import to Alfred

Links
-----

- [Packal](http://www.packal.org/workflow/gauth)

Todo
----

- Add checks and documentation for users without existing config file
- Do not return anything on the time-remaining item
- Try to refresh the time-remaining item each seconds
- Show also the next token
