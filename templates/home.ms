{{! -*- mode: html -*- }}
{{> head }}
  {{ page.content }}

  {{! Loop over blog posts? }}
  <ul>
    {{# site.collections.posts.pages }}
    {{ title }}
    {{/ site.collections.posts.pages }}
  </ul>

{{> tail }}
