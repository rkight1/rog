{{! -*- mode: html -*- }}
{{> head }}

  <h1>{{page.title}}</h2>

  <ul>
  {{# site.collections.tags.valuePages}}
    <li><h3><a href="{{ url }}">{{ title }}</a></h3></li>
  {{/ site.collections.tags.valuePages}}
  </ul>

{{> tail }}
