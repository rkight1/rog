{{! -*- mode: html -*- }}
<!DOCTYPE html>
<html lang="">

<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{page.title}} -- {{site.name}}</title>
  {{! <script src="js/sketch.js"></script> }}
  {{! Load highlight.js }}
  <script src="{{site.baseUrl}}/hljs/highlight.min.js"></script>
  <link rel="stylesheet" href="{{site.baseUrl}}/hljs/styles/monokai.min.css">

  <link rel="stylesheet" href="{{site.baseUrl}}/style.css">

  <script>hljs.highlightAll();</script>
</head>

<body>
  <header id="site-header">
    <h1 id="site-name"><a href="{{site.baseUrl}}">{{site.name}}</a></h1>
    <nav id="site-menu">
      <ul>
        {{# site.collections.menu.pages }}
        <li class="site-menu-item"><a href="{{url}}">{{title}}</a></li>
        {{/ site.collections.menu.pages }}
      </ul>
    </nav>
  </header>
  <main>
