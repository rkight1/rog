{{! -*- mode: html -*- }}
<!DOCTYPE html>
<html lang="">

<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{page.title}} -- {{site.name}}</title>
  <!--<script src="js/sketch.js"></script>-->
  <link rel="stylesheet" href="{{site.baseUrl}}/style.css">
</head>

<body>
  <header id="site-header">
    <a href="{{site.baseUrl}}"><h1>{{site.name}}</h1></a>
    <ul id="site-menu">
      {{# site.collections.menu.pages }}
      <li class="site-menu-item"><a href="{{url}}">{{title}}</a></li>
      {{/ site.collections.menu.pages }}
    </ul>
  </header>
  <main>
