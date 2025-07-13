{{! -*- mode: html -*- }}
{{> head }}
    <h1>Pages tagged <span class="title-tag-name">{{page.collectionName}}</span></h1>
    <ul class="post-list">
    {{#page.collectionPages}}
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
    {{/page.collectionPages}}
    </ul>

{{> tail }}
