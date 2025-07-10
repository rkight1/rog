{{! -*- mode: html -*- }}
{{> head }}

  <h1>{{page.title}}</h2>

  <ul>
  {{# site.collections.tags.valuePages}}
    <li><a href="{{ url }}">{{ title }}</a></li>
  {{/ site.collections.tags.valuePages}}
  </ul>

{{> tail }}
