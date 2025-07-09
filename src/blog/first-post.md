title: First post
date: 2025-07-09
pageType: post
description: This is my first real post!
tags:
  - thing 1
  - thing 2
+++

Welcome to the first post on my blog. At the time of this writing, my SSG is *almost* done. There are still a few more bits and pieces I need to iron out.

## What works:

- Scanning a directory of Markdown files
- Rendering Markdown
- Rendering Mustache templates
- Nearly *all* of the pre-processing required to actually *use* Mustache.


## What I need to finish:

- Some kind of basic command line option processing
  + Mainly to tell it whether to use the *publishing* URL or the *testing* URL
- Syntax highlighting for code samples?

I thought about setting up Pygments for the code highlighting feature, but now I'm leaning more towards JS/CSS front-end solutions like [Prism](https://prismjs.com/) and [highlight.js](https://highlightjs.org/). Those could offer a bit more flexibility and more color schemes. That, and I found the Pygments documentation a bit confusing. I also found some conflicting and vague information about setting and modifying color schemes with Pygments.

After I iron out the remaining details, I should eventually be able to separate the SSG from my blog. It's probably not going to change the world or anything, but it may signal to employers/clients that I know what I'm doing.


## So what's the blog about?

At this point, I'm planning to use it as a dumping ground for ideas, portfolio projects, and maybe more creative things like short stories and art. I'm also going to write about my progress in the [Code Louisville](https://codelouisville.org/) program. If anyone from that program reads this, please note that I am NOT a professional coder in any capacity. I've been playing with code as a hobby for a while, but there are still plenty of gaps in my knowledge.


## About me

I've always had an interest in computers. At first, I viewed them as a form of entertainment. I grew up in the Flash game era, which I still consider the golden age of browser gaming. I remember playing the *Thing Thing Arena* series and watching countless short animations on Newgrounds. I discovered Linux through Debian and Ubuntu back in high school, mainly as a way to escape "browser toolbar hell".

I shared a PC with a relative who wouldn't stop installing random crap from the Internet. Worse still, every time I brought the computer back to a usable state, this relative would undo my work. After complaining about it in a chatroom on Yahoo, someone mentioned Linux and so-called "live" CDs. Basically, I could boot and run an *entirely separate OS* from a CD whenever I needed to use the computer. When I shut the system down and ejected the CD, my dumb relative could go back to their toolbars, pop-ups, and Nigerian princes like I was never there.

After playing with multiple distributions of Linux (KNOPPIX, Puppy, Damn Small, and dozens of others), I eventually figured out how to dual-boot Linux and Windows on the same machine *and* lock my annoying relative out of my stuff. As I continued my Linux journey, I used Windows less and less. Now Linux is my primary OS and has been for years.

My interest in programming grew from using terminal commands. I started with aliases in my `.bashrc` file. Then I wrote some incredibly horrible shell scripts that I won't post here for fear of traumatizing readers. As a remedy to the many downsides of Unix-like shell scripts (performance, readability, functionality, etc), I played with several programming languages over the years. I've mostly settled on Python because of its many libraries and excellent documentation.

I tried to enter the tech sector a few times, but life and misfortune shot me down. It's kind of hard to go to school *and* work to keep a roof over your head. Traditional colleges are slow, and boot camps are expensive. And then whatever skills and knowledge you gain age like milk because the industry moves so fast. And so, I put it all on the back burner and drifted from one dead-end job to another.

Then I got accepted into the Code Louisville program. I'm hoping they can help me cut through the noise and put me on the path to success. My goal right now is to gain multiple streams of income so I won't get derailed by the next COVID-like event.
