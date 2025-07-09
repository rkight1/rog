{{! -*- mode: html -*- }}
{{> head }}
  {{ page.content }}

  {{! Loop over blog posts? }}
  <ul class="post-list">
    {{# site.collections.posts.pages }}
    <li class="post-list-item">
      <a href="{{ url }}"><h2>{{ title }}</h2></a>
      <p class="post-meta">
        Posted on {{ date }} <span class="meta-tags">{{^tags}}Tags: None{{/tags}}{{# tags}}<a href="{{url}}">{{collectionName}}</a>{{/ tags }}
      </p>
      <p class="post-desc">
        {{ description }}
      </p>
    </li>
    {{/ site.collections.posts.pages }}
  </ul>
  {{ site.collections.tags.values }}

{{> tail }}
