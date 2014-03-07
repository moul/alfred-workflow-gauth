Alfred Workflow: Google Authenticator
=====================================

Google Authenticator Workflow for Alfred2

**NOTE:** This is a fork of [Manfred Touron's work](https://github.com/moul/alfred-workflow-gauth) - there aren't big changes, just a couple of bug fixes and new icons to match my environment. 


Installation
------------

Create a `~/.gauth` file with your secrets, ie:

```
[google - bob@gmail.com]
secret=xxxxxxxxxxxxxxxxxx

[evernote - robert]
secret=yyyyyyyyyyyyyyyyyy
```

[Download](https://github.com/golimpio/alfred-workflow-gauth/raw/master/Google%20Authenticator.alfredworkflow) and import to Alfred


Links
-----

- [Packal](http://www.packal.org/workflow/gauth)
- [Manfred Touron's original work](https://github.com/moul/alfred-workflow-gauth)


Acknowledgment
--------------

- Original alarm clock icon
  - [Alex Auda Samora from The Noun Project](http://thenounproject.com/razerk/) 
  - Licensed under Creative Commons Attribution
- Status & signs icons
  - [Hereldar Terkenya](http://hereldar.deviantart.com/)
  - Licensed under a Creative Commons Attribution-Share Alike 3.0 License
- Original source code
  - [Manfred Touron](https://github.com/moul)



Todo
----

- Add ~~checks and~~ documentation for users without existing config file
- ~~Do not return anything on the time-remaining item~~
- Try to refresh the time-remaining item each seconds
- ~~Show also the next token~~
- ~~Add auto complete support~~
- ~~Show all items before typing~~
- ~~Ignore items with wrong key~~ 
