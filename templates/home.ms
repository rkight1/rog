{{! -*- mode: html -*- }}
{{> head }}
  {{ page.content }}

  {{! Loop over blog posts? }}
  <ul>
    {{# site.collections.posts.pages }}
    {{ title }}
    {{ url }}
    {{ date }}
    {{ tags }}
    {{/ site.collections.posts.pages }}
  </ul>

{{> tail }}
