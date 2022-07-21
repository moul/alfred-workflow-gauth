Alfred Workflow: Google Authenticator
=====================================

[![Build Status](https://travis-ci.org/moul/alfred-workflow-gauth.svg?branch=master)](https://travis-ci.org/moul/alfred-workflow-gauth)

An Alfred 2 workflow for Google Authenticator / a.k.a. Two-Factors Authentication / a.k.a. Time-Based Authentication Token / a.k.a. TOTP

![](https://raw.github.com/moul/alfred-workflow-gauth/master/screenshots/anim.gif)
![](https://raw.github.com/moul/alfred-workflow-gauth/master/screenshots/3.png)

An Alfred workflow equivalent of the mobile applications [Google Authenticator](https://itunes.apple.com/en/app/google-authenticator/id388497605?mt=8) and [Authy](https://www.authy.com).

I personally use it on Gmail, Amazon AWS, Github, Facebook, Evernote and Dropbox

A bigger list is available on [Wikipedia](http://en.wikipedia.org/wiki/Two-step_verification)

Installation
------------

Create a `~/.gauth` file with your secrets, ie:

```ini
[google - bob@gmail.com]
secret=xxxxxxxxxxxxxxxxxx

[evernote - robert]
secret=yyyyyyyyyyyyyyyyyy
```

[Download](https://github.com/moul/alfred-workflow-gauth/raw/master/Google%20Authenticator.alfredworkflow) and import to Alfred

Dependencies
------------

- Alfred 2 or 3 with PowerPack
- Python 3.4 or newer

Non-exhaustive list of links for "secret" installation
------------------------------------------------------

- [Google](http://www.google.com/landing/2step/)
- [Dropbox](https://www.dropbox.com/help/363/en)
- [Evernote](http://blog.evernote.com/blog/2013/05/30/evernotes-three-new-security-features/)
- [Github](https://github.com/blog/1614-two-factor-authentication)
- [Amazon AWS](http://aws.amazon.com/iam/details/mfa/)
- [Facebook](https://www.facebook.com/settings?tab=security)

Links
-----

- [Packal: Gauth](http://www.packal.org/workflow/gauth)
- [Official Forum Post](http://www.alfredforum.com/topic/4062-gauth-google-authenticator-time-based-two-factor-authentication/)
- [Source Code](https://github.com/moul/alfred-workflow-gauth/)

Development
-----------

After modifying files locally, run `build.sh` to update the workflow file, and
commit the workflow file update to this repository.

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
- Serial contributor
  - [Gilberto Olimpio](https://github.com/golimpio)

License
-------

MIT
