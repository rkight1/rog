{{! -*- mode: html -*- }}
{{> head }}
  {{{ page.content }}}

  {{! Loop over blog posts? }}
  <ul class="post-list">
    {{# site.collections.posts.pages }}
    <li class="post-list-item">
      <a href="{{ url }}"><h2>{{ title }}</h2></a>
      <p class="post-meta">
        Posted on {{ date }} | Tags: 
        <span class="meta-tags">
          {{^tags}}None{{/tags}}
          {{# tags}}
          <span class="tag-name">
            <a class="tag-name" href="{{url}}">{{collectionName}}</a>
          </span>
          {{/ tags }}
        </span>
      </p>
      {{# description }}
        <p class="post-desc">{{ . }}</p>
      {{/ description }}
    </li>
    {{/ site.collections.posts.pages }}
  </ul>

{{> tail }}
